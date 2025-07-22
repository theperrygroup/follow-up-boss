"""
Tests for EnhancedPeople class including advanced extraction methods,
pond filtering, progress tracking, verification, and export functionality.
"""

import csv
import json
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from follow_up_boss.client import FollowUpBossApiException
from follow_up_boss.enhanced_people import (
    EnhancedPeople,
    extract_all_people,
    extract_pond_people,
    verify_pond_extraction_quick,
)


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleInitialization:
    """Test cases for EnhancedPeople initialization and basic functionality."""

    def test_enhanced_people_initialization(self, mock_robust_client):
        """Test EnhancedPeople initialization."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        assert enhanced_people._client == mock_robust_client
        assert enhanced_people._extraction_stats["total_requests"] == 0
        assert enhanced_people._extraction_stats["total_people_extracted"] == 0
        assert enhanced_people._extraction_stats["extraction_time"] == 0.0
        assert enhanced_people._extraction_stats["last_extraction"] is None

    def test_enhanced_people_inherits_from_people(self, mock_robust_client):
        """Test that EnhancedPeople inherits from base People class."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        # Should have all base People methods
        assert hasattr(enhanced_people, "list_people")
        assert hasattr(enhanced_people, "create_person")
        assert hasattr(enhanced_people, "retrieve_person")
        assert hasattr(enhanced_people, "update_person")
        assert hasattr(enhanced_people, "delete_person")


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleGetAll:
    """Test cases for get_all method with deep pagination."""

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_all_successful_extraction(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test successful get_all extraction."""
        # Mock paginator response
        mock_people = [
            {"id": 1, "name": "Person 1"},
            {"id": 2, "name": "Person 2"},
            {"id": 3, "name": "Person 3"},
        ]

        mock_paginator = Mock()
        mock_paginator.paginate_all.return_value = mock_people
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch("time.time", side_effect=[1000.0, 1005.0]):  # 5 second duration
            results = enhanced_people.get_all(limit=100)

        assert len(results) == 3
        assert results == mock_people

        # Check statistics were updated
        stats = enhanced_people.get_extraction_stats()
        assert stats["total_requests"] == 1
        assert stats["total_people_extracted"] == 3
        assert stats["extraction_time"] == 5.0
        assert stats["last_extraction"] is not None

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_all_with_filters(self, mock_paginator_class, mock_robust_client):
        """Test get_all with custom filters."""
        mock_paginator = Mock()
        mock_paginator.paginate_all.return_value = []
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)
        enhanced_people.get_all(limit=50, tag="important")

        # Verify paginator was called with correct parameters
        mock_paginator_class.assert_called_once_with(
            mock_robust_client, "people", {"limit": 50, "tag": "important"}
        )

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_all_handles_errors(self, mock_paginator_class, mock_robust_client):
        """Test get_all handles pagination errors."""
        mock_paginator = Mock()
        mock_paginator.paginate_all.side_effect = Exception("Pagination failed")
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)

        with pytest.raises(Exception, match="Pagination failed"):
            enhanced_people.get_all()


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleGetByPond:
    """Test cases for pond-specific extraction methods."""

    @patch("follow_up_boss.enhanced_people.PondFilterPaginator")
    def test_get_by_pond_successful_extraction(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test successful get_by_pond extraction."""
        mock_pond_people = [
            {"id": 1, "name": "Person 1", "ponds": [{"id": 134}]},
            {"id": 2, "name": "Person 2", "ponds": [{"id": 134}]},
        ]

        mock_paginator = Mock()
        mock_paginator.paginate_all.return_value = mock_pond_people
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch("time.time", side_effect=[1000.0, 1003.0]):  # 3 second duration
            results = enhanced_people.get_by_pond(134, limit=50)

        assert len(results) == 2
        assert results == mock_pond_people

        # Verify paginator was called with correct pond ID
        mock_paginator_class.assert_called_once_with(
            mock_robust_client, 134, {"limit": 50}
        )

    def test_get_pond_members_comprehensive(self, mock_robust_client):
        """Test get_pond_members_comprehensive delegates to get_by_pond."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch.object(enhanced_people, "get_by_pond") as mock_get_by_pond:
            mock_get_by_pond.return_value = [{"id": 1}]

            result = enhanced_people.get_pond_members_comprehensive(134)

            mock_get_by_pond.assert_called_once_with(134)
            assert result == [{"id": 1}]


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleGetConcurrent:
    """Test cases for concurrent processing."""

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_concurrent_successful_extraction(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test successful concurrent extraction."""
        mock_people = [{"id": 1}, {"id": 2}, {"id": 3}]

        mock_paginator = Mock()
        mock_paginator.paginate_concurrent.return_value = mock_people
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch("time.time", side_effect=[1000.0, 1002.0]):  # 2 second duration
            results = enhanced_people.get_concurrent(max_workers=5, limit=100)

        assert len(results) == 3
        assert results == mock_people

        # Verify paginate_concurrent was called with correct parameters
        mock_paginator.paginate_concurrent.assert_called_once_with(max_workers=5)


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleGetWithProgress:
    """Test cases for progress tracking functionality."""

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_with_progress_with_callback(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test get_with_progress with progress callback."""
        mock_people = [{"id": 1}, {"id": 2}]

        # Mock strategy that yields responses
        mock_strategy = Mock()
        mock_strategy.paginate.return_value = iter(
            [{"people": [{"id": 1}]}, {"people": [{"id": 2}]}]
        )

        mock_paginator = Mock()
        mock_paginator.strategies = [lambda *args: mock_strategy]
        mock_paginator._extract_items.side_effect = lambda r: r.get("people", [])
        mock_paginator_class.return_value = mock_paginator

        # Track callback calls
        callback_calls = []

        def progress_callback(current, total, elapsed):
            callback_calls.append((current, total, elapsed))

        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch("time.time", side_effect=[1000.0, 1001.0, 1002.0, 1003.0]):
            results = enhanced_people.get_with_progress(
                callback=progress_callback, limit=100
            )

        assert len(results) == 2
        assert len(callback_calls) >= 2  # Should have called callback multiple times

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_with_progress_without_callback(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test get_with_progress without callback."""
        mock_people = [{"id": 1}]

        mock_strategy = Mock()
        mock_strategy.paginate.return_value = iter([{"people": [{"id": 1}]}])

        mock_paginator = Mock()
        mock_paginator.strategies = [lambda *args: mock_strategy]
        mock_paginator._extract_items.return_value = [{"id": 1}]
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)
        results = enhanced_people.get_with_progress()

        assert len(results) == 1


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleSampling:
    """Test cases for pond sampling functionality."""

    def test_extract_pond_sample_successful(self, mock_robust_client):
        """Test successful pond sample extraction."""
        mock_response = {
            "people": [{"id": 1, "name": "Sample 1"}, {"id": 2, "name": "Sample 2"}]
        }

        mock_robust_client._get.return_value = mock_response

        enhanced_people = EnhancedPeople(mock_robust_client)
        results = enhanced_people.extract_pond_sample(134, 10)

        assert len(results) == 2
        assert results == mock_response["people"]

        # Verify correct API call was made
        mock_robust_client._get.assert_called_once_with(
            "people", params={"pond": 134, "limit": 10}
        )

    def test_extract_pond_sample_default_size(self, mock_robust_client):
        """Test pond sample extraction with default size."""
        mock_robust_client._get.return_value = {"people": []}

        enhanced_people = EnhancedPeople(mock_robust_client)
        enhanced_people.extract_pond_sample(134)

        # Should use default sample size of 100
        mock_robust_client._get.assert_called_once_with(
            "people", params={"pond": 134, "limit": 100}
        )


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleVerification:
    """Test cases for pond extraction verification."""

    def test_verify_pond_extraction_successful(self, mock_robust_client):
        """Test successful pond extraction verification."""
        # Mock sample extraction
        sample_people = [{"id": 1, "ponds": [{"id": 134}]}]

        # Mock comprehensive extraction
        comprehensive_people = [
            {"id": 1, "ponds": [{"id": 134}]},
            {"id": 2, "ponds": [{"id": 134}]},
            {"id": 3, "ponds": [{"id": 134}]},
        ]

        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch.object(
            enhanced_people, "extract_pond_sample"
        ) as mock_sample, patch.object(
            enhanced_people, "get_by_pond"
        ) as mock_get_by_pond:
            mock_sample.return_value = sample_people
            mock_get_by_pond.return_value = comprehensive_people

            with patch("time.time", side_effect=[1000.0, 1005.0]):  # 5 second duration
                results = enhanced_people.verify_pond_extraction(134, expected_count=3)

        assert results["pond_id"] == 134
        assert results["expected_count"] == 3
        assert results["verification_passed"] is True
        assert results["extraction_methods"]["sample"]["count"] == 1
        assert results["extraction_methods"]["comprehensive"]["count"] == 3
        assert results["pond_membership_verified"] is True
        assert results["accuracy"] == 1.0  # 3/3 = 100%
        assert results["recommendation"] == "Extraction working correctly"

    def test_verify_pond_extraction_accuracy_below_threshold(self, mock_robust_client):
        """Test verification when accuracy is below threshold."""
        # Mock extractions with lower accuracy
        sample_people = [{"id": 1, "ponds": [{"id": 134}]}]
        comprehensive_people = [
            {"id": 1, "ponds": [{"id": 134}]}
        ]  # Only 1 out of expected 1000

        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch.object(
            enhanced_people, "extract_pond_sample"
        ) as mock_sample, patch.object(
            enhanced_people, "get_by_pond"
        ) as mock_get_by_pond:
            mock_sample.return_value = sample_people
            mock_get_by_pond.return_value = comprehensive_people

            results = enhanced_people.verify_pond_extraction(134, expected_count=1000)

        assert results["verification_passed"] is False
        assert results["accuracy"] == 0.001  # 1/1000 = 0.1%
        assert results["recommendation"] == "Manual investigation required"

    def test_verify_pond_extraction_handles_errors(self, mock_robust_client):
        """Test verification handles errors gracefully."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        with patch.object(enhanced_people, "extract_pond_sample") as mock_sample:
            mock_sample.side_effect = Exception("Sample extraction failed")

            results = enhanced_people.verify_pond_extraction(134)

        assert "error" in results
        assert results["recommendation"] == "Check API connectivity and permissions"


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleExport:
    """Test cases for data export functionality."""

    def test_export_to_csv_successful(self, mock_robust_client, temp_csv_file):
        """Test successful CSV export."""
        test_people = [
            {
                "id": 1,
                "firstName": "John",
                "lastName": "Doe",
                "emails": [{"value": "john@example.com"}],
            },
            {
                "id": 2,
                "firstName": "Jane",
                "lastName": "Smith",
                "emails": [{"value": "jane@example.com"}],
            },
        ]

        enhanced_people = EnhancedPeople(mock_robust_client)
        result_path = enhanced_people.export_to_csv(test_people, temp_csv_file)

        assert result_path == os.path.abspath(temp_csv_file)
        assert os.path.exists(temp_csv_file)

        # Verify CSV content
        with open(temp_csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["firstName"] == "John"
        assert rows[1]["firstName"] == "Jane"

    def test_export_to_csv_handles_complex_fields(
        self, mock_robust_client, temp_csv_file
    ):
        """Test CSV export handles complex fields (lists, dicts)."""
        test_people = [
            {
                "id": 1,
                "emails": [{"value": "test@example.com"}],  # List
                "address": {"street": "123 Main St", "city": "Anytown"},  # Dict
            }
        ]

        enhanced_people = EnhancedPeople(mock_robust_client)
        enhanced_people.export_to_csv(test_people, temp_csv_file)

        # Verify complex fields are stringified
        with open(temp_csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert "[{'value': 'test@example.com'}]" in row["emails"]
        assert "{'street': '123 Main St', 'city': 'Anytown'}" in row["address"]

    def test_export_to_csv_empty_data_error(self, mock_robust_client, temp_csv_file):
        """Test CSV export with empty data raises error."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        with pytest.raises(ValueError, match="No people data to export"):
            enhanced_people.export_to_csv([], temp_csv_file)

    def test_export_to_json_successful(self, mock_robust_client, temp_json_file):
        """Test successful JSON export."""
        test_people = [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]

        enhanced_people = EnhancedPeople(mock_robust_client)
        result_path = enhanced_people.export_to_json(test_people, temp_json_file)

        assert result_path == os.path.abspath(temp_json_file)
        assert os.path.exists(temp_json_file)

        # Verify JSON content
        with open(temp_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[0]["name"] == "John Doe"
        assert data[1]["name"] == "Jane Smith"

    def test_export_to_json_empty_data_error(self, mock_robust_client, temp_json_file):
        """Test JSON export with empty data raises error."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        with pytest.raises(ValueError, match="No people data to export"):
            enhanced_people.export_to_json([], temp_json_file)


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleStatistics:
    """Test cases for extraction statistics tracking."""

    def test_get_extraction_stats_initial_state(self, mock_robust_client):
        """Test initial extraction statistics."""
        enhanced_people = EnhancedPeople(mock_robust_client)
        stats = enhanced_people.get_extraction_stats()

        assert stats["total_requests"] == 0
        assert stats["total_people_extracted"] == 0
        assert stats["extraction_time"] == 0.0
        assert stats["last_extraction"] is None

    def test_extraction_stats_isolation(self, mock_robust_client):
        """Test that stats returned are a copy (isolation)."""
        enhanced_people = EnhancedPeople(mock_robust_client)

        stats1 = enhanced_people.get_extraction_stats()
        stats1["total_requests"] = 999  # Modify the returned dict

        stats2 = enhanced_people.get_extraction_stats()
        assert stats2["total_requests"] == 0  # Should not be affected


@pytest.mark.unit
@pytest.mark.enhanced
class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    @patch("follow_up_boss.enhanced_people.RobustApiClient")
    @patch("follow_up_boss.enhanced_people.EnhancedPeople")
    def test_extract_all_people_with_default_client(
        self, mock_enhanced_people_class, mock_client_class
    ):
        """Test extract_all_people with default client creation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_enhanced_people = Mock()
        mock_enhanced_people.get_all.return_value = [{"id": 1}]
        mock_enhanced_people_class.return_value = mock_enhanced_people

        result = extract_all_people()

        assert result == [{"id": 1}]
        mock_client_class.assert_called_once()
        mock_enhanced_people_class.assert_called_once_with(mock_client)
        mock_enhanced_people.get_all.assert_called_once()

    def test_extract_all_people_with_provided_client(self, mock_robust_client):
        """Test extract_all_people with provided client."""
        with patch(
            "follow_up_boss.enhanced_people.EnhancedPeople"
        ) as mock_enhanced_people_class:
            mock_enhanced_people = Mock()
            mock_enhanced_people.get_all.return_value = [{"id": 1}]
            mock_enhanced_people_class.return_value = mock_enhanced_people

            result = extract_all_people(client=mock_robust_client)

            assert result == [{"id": 1}]
            mock_enhanced_people_class.assert_called_once_with(mock_robust_client)

    @patch("follow_up_boss.enhanced_people.RobustApiClient")
    @patch("follow_up_boss.enhanced_people.EnhancedPeople")
    def test_extract_pond_people_with_default_client(
        self, mock_enhanced_people_class, mock_client_class
    ):
        """Test extract_pond_people with default client creation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_enhanced_people = Mock()
        mock_enhanced_people.get_by_pond.return_value = [
            {"id": 1, "ponds": [{"id": 134}]}
        ]
        mock_enhanced_people_class.return_value = mock_enhanced_people

        result = extract_pond_people(134)

        assert len(result) == 1
        mock_enhanced_people.get_by_pond.assert_called_once_with(134)

    @patch("follow_up_boss.enhanced_people.RobustApiClient")
    @patch("follow_up_boss.enhanced_people.EnhancedPeople")
    def test_verify_pond_extraction_quick(
        self, mock_enhanced_people_class, mock_client_class
    ):
        """Test verify_pond_extraction_quick convenience function."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_enhanced_people = Mock()
        mock_verification_result = {"verification_passed": True, "pond_id": 134}
        mock_enhanced_people.verify_pond_extraction.return_value = (
            mock_verification_result
        )
        mock_enhanced_people_class.return_value = mock_enhanced_people

        result = verify_pond_extraction_quick(134, 1000)

        assert result == mock_verification_result
        mock_enhanced_people.verify_pond_extraction.assert_called_once_with(134, 1000)


@pytest.mark.integration
@pytest.mark.enhanced
class TestEnhancedPeopleIntegration:
    """Integration tests for EnhancedPeople with real API calls."""

    def test_extract_pond_sample_real_api(self, enhanced_people):
        """Test pond sample extraction with real API."""
        # Use a small sample to avoid hitting rate limits
        results = enhanced_people.extract_pond_sample(134, 3)

        # Results should be a list (may be empty)
        assert isinstance(results, list)

        # If we got results, verify structure
        for person in results:
            assert "id" in person
            assert isinstance(person["id"], int)

    @pytest.mark.slow
    def test_get_all_real_api_small_limit(self, enhanced_people):
        """Test get_all with real API using small limit."""
        results = enhanced_people.get_all(limit=5)

        assert isinstance(results, list)

        # Verify extraction stats were updated
        stats = enhanced_people.get_extraction_stats()
        assert stats["total_requests"] >= 1
        assert stats["total_people_extracted"] == len(results)
        assert stats["extraction_time"] > 0
        assert stats["last_extraction"] is not None

    def test_verify_pond_extraction_real_api(self, enhanced_people):
        """Test pond verification with real API."""
        # This should work even if pond is empty
        results = enhanced_people.verify_pond_extraction(134)

        assert "pond_id" in results
        assert "verification_passed" in results
        assert "extraction_methods" in results
        assert "recommendation" in results
        assert results["pond_id"] == 134

    @pytest.mark.slow
    def test_export_functionality_real_data(
        self, enhanced_people, temp_csv_file, temp_json_file
    ):
        """Test export functionality with real API data."""
        # Get a small sample of real data
        sample_data = enhanced_people.extract_pond_sample(134, 2)

        if sample_data:  # Only test if we have data
            # Test CSV export
            csv_path = enhanced_people.export_to_csv(sample_data, temp_csv_file)
            assert os.path.exists(csv_path)

            # Test JSON export
            json_path = enhanced_people.export_to_json(sample_data, temp_json_file)
            assert os.path.exists(json_path)

            # Verify files have content
            assert os.path.getsize(csv_path) > 0
            assert os.path.getsize(json_path) > 0


@pytest.mark.unit
@pytest.mark.enhanced
class TestEnhancedPeopleErrorHandling:
    """Test error handling in various scenarios."""

    @patch("follow_up_boss.enhanced_people.SmartPaginator")
    def test_get_all_logs_and_reraises_errors(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test get_all properly logs and re-raises errors."""
        mock_paginator = Mock()
        mock_paginator.paginate_all.side_effect = Exception("Pagination error")
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)

        with pytest.raises(Exception, match="Pagination error"):
            enhanced_people.get_all()

    @patch("follow_up_boss.enhanced_people.PondFilterPaginator")
    def test_get_by_pond_logs_and_reraises_errors(
        self, mock_paginator_class, mock_robust_client
    ):
        """Test get_by_pond properly logs and re-raises errors."""
        mock_paginator = Mock()
        mock_paginator.paginate_all.side_effect = Exception("Pond extraction error")
        mock_paginator_class.return_value = mock_paginator

        enhanced_people = EnhancedPeople(mock_robust_client)

        with pytest.raises(Exception, match="Pond extraction error"):
            enhanced_people.get_by_pond(134)

    def test_extract_pond_sample_logs_and_reraises_errors(self, mock_robust_client):
        """Test extract_pond_sample properly logs and re-raises errors."""
        mock_robust_client._get.side_effect = Exception("API error")

        enhanced_people = EnhancedPeople(mock_robust_client)

        with pytest.raises(Exception, match="API error"):
            enhanced_people.extract_pond_sample(134)

    def test_export_to_csv_handles_file_permissions(self, mock_robust_client):
        """Test CSV export handles file permission errors."""
        test_people = [{"id": 1, "name": "Test"}]
        enhanced_people = EnhancedPeople(mock_robust_client)

        # Try to write to a directory that doesn't exist
        invalid_path = "/nonexistent/directory/file.csv"

        with pytest.raises((OSError, FileNotFoundError, PermissionError)):
            enhanced_people.export_to_csv(test_people, invalid_path)
