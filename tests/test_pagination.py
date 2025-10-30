"""
Tests for pagination functionality including SmartPaginator, PondFilterPaginator,
and all pagination strategies (Offset, DateRange, NextLink).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from follow_up_boss.client import FollowUpBossApiException
from follow_up_boss.pagination import (
    DateRangeStrategy,
    NextLinkStrategy,
    OffsetPaginationStrategy,
    PaginationStrategy,
    PondFilterPaginator,
    SmartPaginator,
)


@pytest.mark.unit
@pytest.mark.pagination
class TestPaginationStrategy:
    """Test cases for base PaginationStrategy class."""

    def test_base_strategy_initialization(self):
        """Test base strategy initialization."""
        mock_client = Mock()
        strategy = PaginationStrategy(mock_client, "people", {"limit": 100})

        assert strategy.client == mock_client
        assert strategy.endpoint == "people"
        assert strategy.params == {"limit": 100}
        assert strategy.offset_limit == 2000

    def test_base_strategy_paginate_not_implemented(self):
        """Test that base strategy paginate method raises NotImplementedError."""
        mock_client = Mock()
        strategy = PaginationStrategy(mock_client, "people")

        with pytest.raises(NotImplementedError):
            list(strategy.paginate())


@pytest.mark.unit
@pytest.mark.pagination
class TestOffsetPaginationStrategy:
    """Test cases for OffsetPaginationStrategy."""

    def test_offset_strategy_initialization(self):
        """Test offset strategy initialization."""
        mock_client = Mock()
        params = {"limit": 50, "offset": 100}
        strategy = OffsetPaginationStrategy(mock_client, "people", params)

        assert strategy.client == mock_client
        assert strategy.endpoint == "people"
        assert strategy.params == params

    def test_offset_strategy_successful_pagination(self):
        """Test successful offset pagination."""
        mock_client = Mock()

        # Mock responses for pagination
        responses = [
            {
                "people": [{"id": i} for i in range(1, 51)],
                "_metadata": {"total": 200},
            },  # First page
            {
                "people": [{"id": i} for i in range(51, 101)],
                "_metadata": {"total": 200},
            },  # Second page
            {
                "people": [{"id": i} for i in range(101, 121)],
                "_metadata": {"total": 200},
            },  # Last page (partial)
        ]

        mock_client._get.side_effect = responses

        strategy = OffsetPaginationStrategy(mock_client, "people", {"limit": 50})
        results = list(strategy.paginate())

        assert len(results) == 3
        assert len(results[0]["people"]) == 50
        assert len(results[1]["people"]) == 50
        assert len(results[2]["people"]) == 20  # Partial page indicates end

    def test_offset_strategy_deep_pagination_limit(self):
        """Test offset strategy stops at deep pagination limit."""
        mock_client = Mock()

        # Mock responses that would trigger deep pagination error
        def mock_get_side_effect(endpoint, params=None):
            offset = params.get("offset", 0)
            if offset >= 2000:
                raise FollowUpBossApiException(
                    "Deep pagination disabled, use 'nextLink' url"
                )
            return {"people": [{"id": i} for i in range(offset + 1, offset + 101)]}

        mock_client._get.side_effect = mock_get_side_effect

        strategy = OffsetPaginationStrategy(mock_client, "people", {"limit": 100})
        results = list(strategy.paginate())

        # Should stop before hitting the limit
        assert len(results) == 20  # 20 pages of 100 items = 2000 items

    def test_offset_strategy_handles_deep_pagination_error(self):
        """Test offset strategy handles deep pagination error gracefully."""
        mock_client = Mock()

        # First call succeeds, second fails with deep pagination error
        mock_client._get.side_effect = [
            {"people": [{"id": i} for i in range(1, 101)]},
            FollowUpBossApiException("Deep pagination disabled, use 'nextLink' url"),
        ]

        strategy = OffsetPaginationStrategy(mock_client, "people", {"limit": 100})
        results = list(strategy.paginate())

        # Should get only the first page
        assert len(results) == 1

    def test_get_items_key_detection(self):
        """Test _get_items_key method correctly identifies response keys."""
        mock_client = Mock()
        strategy = OffsetPaginationStrategy(mock_client, "people")

        # Test various response formats
        test_cases = [
            ({"people": []}, "people"),
            ({"deals": []}, "deals"),
            ({"events": []}, "events"),
            ({"unknown": []}, None),
            ({"data": []}, None),  # Not a known key
        ]

        for response, expected_key in test_cases:
            result = strategy._get_items_key(response)
            assert result == expected_key


@pytest.mark.unit
@pytest.mark.pagination
class TestDateRangeStrategy:
    """Test cases for DateRangeStrategy."""

    def test_date_range_strategy_initialization(self):
        """Test date range strategy initialization."""
        mock_client = Mock()
        strategy = DateRangeStrategy(
            mock_client, "people", {"limit": 100}, date_field="updated", chunk_days=7
        )

        assert strategy.date_field == "updated"
        assert strategy.chunk_days == 7

    def test_date_range_strategy_default_date_range(self):
        """Test date range strategy with default date range."""
        mock_client = Mock()
        mock_client._get.return_value = {"people": []}

        strategy = DateRangeStrategy(mock_client, "people")

        # Mock the offset strategy to avoid infinite recursion
        with patch(
            "follow_up_boss.pagination.OffsetPaginationStrategy"
        ) as mock_offset_strategy:
            mock_offset_instance = Mock()
            mock_offset_instance.paginate.return_value = iter([{"people": []}])
            mock_offset_strategy.return_value = mock_offset_instance

            results = list(strategy.paginate())

            # Should have made at least one call
            assert len(results) >= 0
            assert mock_offset_strategy.called

    def test_date_range_strategy_custom_date_range(self):
        """Test date range strategy with custom start date."""
        mock_client = Mock()
        start_date = datetime.now() - timedelta(days=30)
        params = {"start_date": start_date.isoformat()}

        strategy = DateRangeStrategy(mock_client, "people", params, chunk_days=10)

        with patch(
            "follow_up_boss.pagination.OffsetPaginationStrategy"
        ) as mock_offset_strategy:
            mock_offset_instance = Mock()
            mock_offset_instance.paginate.return_value = iter([{"people": []}])
            mock_offset_strategy.return_value = mock_offset_instance

            results = list(strategy.paginate())

            # Should have made calls with date parameters
            assert mock_offset_strategy.called
            call_args = mock_offset_strategy.call_args[0]
            call_params = call_args[2]  # Third argument is params
            assert "created_start" in call_params or "updated_start" in call_params


@pytest.mark.unit
@pytest.mark.pagination
class TestNextLinkStrategy:
    """Test cases for NextLinkStrategy."""

    def test_nextlink_strategy_initialization(self):
        """Test NextLink strategy initialization."""
        mock_client = Mock()
        strategy = NextLinkStrategy(mock_client, "people", {"limit": 100})

        assert strategy.client == mock_client
        assert strategy.endpoint == "people"
        assert strategy.params == {"limit": 100}

    def test_nextlink_strategy_with_next_links(self):
        """Test NextLink strategy following pagination links."""
        mock_client = Mock()

        # Mock responses with nextLink URLs
        responses = [
            {
                "people": [{"id": i} for i in range(1, 51)],
                "_metadata": {
                    "nextLink": "https://api.example.com/people?offset=50&limit=50"
                },
            },
            {
                "people": [{"id": i} for i in range(51, 101)],
                "_metadata": {
                    "nextLink": "https://api.example.com/people?offset=100&limit=50"
                },
            },
            {
                "people": [{"id": i} for i in range(101, 121)],
                "_metadata": {},  # No nextLink - end of data
            },
        ]

        mock_client._get.side_effect = responses

        strategy = NextLinkStrategy(mock_client, "people", {"limit": 50})
        results = list(strategy.paginate())

        assert len(results) == 3
        assert mock_client._get.call_count == 3

    def test_nextlink_strategy_without_next_links(self):
        """Test NextLink strategy when no nextLink is provided."""
        mock_client = Mock()
        mock_client._get.return_value = {
            "people": [{"id": 1}],
            "_metadata": {},  # No nextLink
        }

        strategy = NextLinkStrategy(mock_client, "people")
        results = list(strategy.paginate())

        # Should get only one page
        assert len(results) == 1
        assert mock_client._get.call_count == 1

    def test_extract_next_link_various_formats(self):
        """Test _extract_next_link handles various response formats."""
        mock_client = Mock()
        strategy = NextLinkStrategy(mock_client, "people")

        test_cases = [
            (
                {"_metadata": {"nextLink": "http://example.com/next"}},
                "http://example.com/next",
            ),
            (
                {"_metadata": {"next": "http://example.com/next2"}},
                "http://example.com/next2",
            ),
            ({"nextLink": "http://example.com/next3"}, "http://example.com/next3"),
            ({"_metadata": {}}, None),
            ({}, None),
        ]

        for response, expected_link in test_cases:
            result = strategy._extract_next_link(response)
            assert result == expected_link

    def test_parse_next_link_url(self):
        """Test _parse_next_link correctly parses URL parameters."""
        mock_client = Mock()
        strategy = NextLinkStrategy(mock_client, "people")

        test_url = "https://api.example.com/people?offset=100&limit=50&sort=name"
        result = strategy._parse_next_link(test_url)

        # offset and limit are converted to integers
        assert result["offset"] == 100
        assert result["limit"] == 50
        assert result["sort"] == "name"


@pytest.mark.unit
@pytest.mark.pagination
class TestSmartPaginator:
    """Test cases for SmartPaginator intelligence."""

    def test_smart_paginator_initialization(self):
        """Test SmartPaginator initialization."""
        mock_client = Mock()
        paginator = SmartPaginator(mock_client, "people", {"limit": 100})

        assert paginator.client == mock_client
        assert paginator.endpoint == "people"
        assert paginator.params == {"limit": 100}
        assert paginator.offset_limit == 2000
        assert len(paginator.strategies) == 3

    def test_smart_paginator_tries_strategies_in_order(self):
        """Test SmartPaginator tries strategies in order until one succeeds."""
        mock_client = Mock()

        # Create mock strategy classes
        mock_offset = Mock()
        mock_offset_instance = Mock()
        mock_offset_instance.paginate.side_effect = Exception("Offset failed")
        mock_offset.return_value = mock_offset_instance

        mock_nextlink = Mock()
        mock_nextlink_instance = Mock()
        mock_nextlink_instance.paginate.return_value = iter([{"people": [{"id": 1}]}])
        mock_nextlink.return_value = mock_nextlink_instance

        mock_daterange = Mock()
        mock_daterange_instance = Mock()
        mock_daterange.return_value = mock_daterange_instance

        # Create paginator and inject mocked strategies
        paginator = SmartPaginator(mock_client, "people")
        paginator.strategies = [mock_offset, mock_nextlink, mock_daterange]

        results = paginator.paginate_all()

        assert len(results) == 1
        assert results[0]["id"] == 1
        assert mock_offset.called
        assert mock_nextlink.called
        assert not mock_daterange.called

    def test_smart_paginator_extract_items(self):
        """Test SmartPaginator _extract_items method."""
        mock_client = Mock()
        paginator = SmartPaginator(mock_client, "people")

        test_cases = [
            ({"people": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
            ({"deals": [{"id": 3}]}, [{"id": 3}]),
            ({"unknown": [{"id": 4}]}, []),
            ({}, []),
        ]

        for response, expected_items in test_cases:
            result = paginator._extract_items(response)
            assert result == expected_items

    def test_smart_paginator_get_total_count(self):
        """Test SmartPaginator _get_total_count method."""
        mock_client = Mock()
        paginator = SmartPaginator(mock_client, "people")

        test_cases = [
            ({"_metadata": {"total": 1000}}, 1000),
            ({"_metadata": {"totalCount": 2000}}, 2000),
            ({"_metadata": {}}, None),
            ({}, None),
        ]

        for response, expected_count in test_cases:
            result = paginator._get_total_count(response)
            assert result == expected_count

    def test_smart_paginator_deduplication(self):
        """Test SmartPaginator removes duplicate items by ID."""
        mock_client = Mock()

        with patch("follow_up_boss.pagination.OffsetPaginationStrategy") as mock_offset:
            # Mock strategy that returns duplicate items
            responses = [
                {"people": [{"id": 1, "name": "Person 1"}]},
                {
                    "people": [
                        {"id": 1, "name": "Person 1"},
                        {"id": 2, "name": "Person 2"},
                    ]
                },
                {
                    "people": [
                        {"id": 2, "name": "Person 2"},
                        {"id": 3, "name": "Person 3"},
                    ]
                },
            ]

            mock_offset_instance = Mock()
            mock_offset_instance.paginate.return_value = iter(responses)
            mock_offset.return_value = mock_offset_instance

            paginator = SmartPaginator(mock_client, "people")
            results = paginator.paginate_all()

            # Should have 3 unique items
            assert len(results) == 3
            ids = [item["id"] for item in results]
            assert ids == [1, 2, 3]

    @patch("follow_up_boss.pagination.ThreadPoolExecutor")
    def test_smart_paginator_concurrent_processing(self, mock_executor):
        """Test SmartPaginator concurrent processing."""
        from unittest.mock import MagicMock

        mock_client = Mock()

        # Mock the executor and futures - use MagicMock for context manager support
        mock_future = Mock()
        mock_future.result.return_value = [{"id": 1}, {"id": 2}]
        mock_executor_instance = MagicMock()
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.__exit__.return_value = None
        mock_executor_instance.submit.return_value = mock_future
        mock_executor.return_value = mock_executor_instance

        # Mock as_completed
        with patch("follow_up_boss.pagination.as_completed") as mock_as_completed:
            mock_as_completed.return_value = [mock_future]

            # Mock initial response to get total count
            mock_client._get.return_value = {"_metadata": {"total": 500}, "people": []}

            paginator = SmartPaginator(mock_client, "people")
            results = paginator.paginate_concurrent(max_workers=3)

            assert len(results) == 2
            assert mock_executor.called


@pytest.mark.unit
@pytest.mark.pagination
class TestPondFilterPaginator:
    """Test cases for PondFilterPaginator functionality."""

    def test_pond_filter_paginator_initialization(self):
        """Test PondFilterPaginator initialization."""
        mock_client = Mock()
        paginator = PondFilterPaginator(mock_client, 134, {"limit": 100})

        assert paginator.pond_id == 134
        assert paginator.params["pond"] == 134
        assert paginator.params["limit"] == 100

    def test_pond_filter_paginator_verify_filtering_success(self):
        """Test pond filtering verification when API filtering works."""
        mock_client = Mock()
        paginator = PondFilterPaginator(mock_client, 134)

        # Mock people data where all people are in the correct pond
        test_people = [
            {"id": 1, "ponds": [{"id": 134}]},
            {"id": 2, "ponds": [{"id": 134}]},
            {"id": 3, "ponds": [{"id": 134}]},
        ]

        result = paginator._verify_pond_results(test_people)
        assert result is True

    def test_pond_filter_paginator_verify_filtering_failure(self):
        """Test pond filtering verification when API filtering fails."""
        mock_client = Mock()
        paginator = PondFilterPaginator(mock_client, 134)

        # Mock people data where some people are NOT in the correct pond
        test_people = [
            {"id": 1, "ponds": [{"id": 134}]},
            {"id": 2, "ponds": [{"id": 135}]},  # Wrong pond
            {"id": 3, "ponds": [{"id": 134}]},
        ]

        result = paginator._verify_pond_results(test_people)
        assert result is False

    def test_pond_filter_paginator_verify_empty_results(self):
        """Test pond filtering verification with empty results."""
        mock_client = Mock()
        paginator = PondFilterPaginator(mock_client, 134)

        # With strict=False, empty results are considered valid
        result = paginator._verify_pond_results([], strict=False)
        assert result is True  # Empty results are valid in non-strict mode

        # With strict=True (default), empty results fail verification
        result_strict = paginator._verify_pond_results([])
        assert result_strict is False

    def test_person_in_pond_various_formats(self):
        """Test _person_in_pond handles various pond data formats."""
        mock_client = Mock()
        paginator = PondFilterPaginator(mock_client, 134)

        test_cases = [
            # List of pond objects
            ({"ponds": [{"id": 134}, {"id": 135}]}, True),
            ({"ponds": [{"id": 135}, {"id": 136}]}, False),
            # List of pond IDs
            ({"ponds": [134, 135]}, True),
            ({"ponds": [135, 136]}, False),
            # Single pond object
            ({"ponds": {"id": 134}}, True),
            ({"ponds": {"id": 135}}, False),
            # Single pond ID
            ({"ponds": 134}, True),
            ({"ponds": 135}, False),
            # No ponds
            ({"ponds": []}, False),
            ({}, False),
        ]

        for person_data, expected_result in test_cases:
            result = paginator._person_in_pond(person_data, 134)
            assert result == expected_result

    def test_pond_filter_paginator_fallback_to_post_filtering(self):
        """Test pond paginator falls back to post-fetch filtering."""
        mock_client = Mock()

        with patch.object(PondFilterPaginator, "_verify_pond_results") as mock_verify:
            # Mock verification to fail (indicating API filtering didn't work)
            mock_verify.return_value = False

            with patch.object(
                PondFilterPaginator, "_fetch_and_filter_locally"
            ) as mock_fetch_filter:
                mock_fetch_filter.return_value = [{"id": 1, "ponds": [{"id": 134}]}]

                paginator = PondFilterPaginator(mock_client, 134)
                results = paginator.paginate_all()

                assert len(results) == 1
                assert mock_fetch_filter.called

    def test_fetch_and_filter_locally_method(self):
        """Test _fetch_and_filter_locally method."""
        mock_client = Mock()

        with patch("follow_up_boss.pagination.SmartPaginator") as mock_smart_paginator:
            # Mock all people data (mix of different ponds)
            all_people = [
                {"id": 1, "ponds": [{"id": 134}]},
                {"id": 2, "ponds": [{"id": 135}]},
                {"id": 3, "ponds": [{"id": 134}]},
                {"id": 4, "ponds": [{"id": 136}]},
            ]

            mock_paginator_instance = Mock()
            mock_paginator_instance.paginate_all.return_value = all_people
            mock_smart_paginator.return_value = mock_paginator_instance

            paginator = PondFilterPaginator(mock_client, 134)
            results = paginator._fetch_and_filter_locally()

            # Should only return people from pond 134
            assert len(results) == 2
            assert all(paginator._person_in_pond(person, 134) for person in results)


@pytest.mark.integration
@pytest.mark.pagination
class TestPaginationIntegration:
    """Integration tests for pagination with real API calls."""

    @pytest.mark.slow
    def test_smart_paginator_real_api(self, robust_client):
        """Test SmartPaginator with real API calls."""
        paginator = SmartPaginator(robust_client, "people", {"limit": 5})

        results = paginator.paginate_all()

        assert isinstance(results, list)
        # Should get some results (or empty list if no people)
        for person in results:
            assert "id" in person

    def test_offset_strategy_real_api(self, robust_client):
        """Test OffsetPaginationStrategy with real API calls."""
        strategy = OffsetPaginationStrategy(robust_client, "people", {"limit": 5})

        responses = list(strategy.paginate())

        assert len(responses) >= 1
        for response in responses:
            assert "_metadata" in response or "people" in response

    def test_pond_filter_paginator_real_api(self, robust_client):
        """Test PondFilterPaginator with real API calls."""
        # Use a pond ID that likely exists (or test will pass with empty results)
        paginator = PondFilterPaginator(robust_client, 134, {"limit": 5})

        results = paginator.paginate_all()

        # Results should be a list (may be empty)
        assert isinstance(results, list)

        # If we got results, they should be in the correct pond
        for person in results[:3]:  # Check first 3 people
            assert paginator._person_in_pond(person, 134)


@pytest.mark.unit
@pytest.mark.pagination
class TestPaginationErrorHandling:
    """Test error handling in pagination scenarios."""

    def test_smart_paginator_all_strategies_fail(self):
        """Test SmartPaginator when all strategies fail."""
        mock_client = Mock()

        with patch(
            "follow_up_boss.pagination.OffsetPaginationStrategy"
        ) as mock_offset, patch(
            "follow_up_boss.pagination.NextLinkStrategy"
        ) as mock_nextlink, patch(
            "follow_up_boss.pagination.DateRangeStrategy"
        ) as mock_daterange:
            # All strategies fail
            for mock_strategy in [mock_offset, mock_nextlink, mock_daterange]:
                mock_instance = Mock()
                mock_instance.paginate.side_effect = Exception("Strategy failed")
                mock_strategy.return_value = mock_instance

            paginator = SmartPaginator(mock_client, "people")

            with pytest.raises(RuntimeError, match="All pagination strategies failed"):
                paginator.paginate_all()

    def test_offset_strategy_handles_exceptions(self):
        """Test OffsetPaginationStrategy handles various exceptions."""
        mock_client = Mock()

        # Mock client that raises different exceptions
        mock_client._get.side_effect = [
            {"people": [{"id": 1}]},  # First call succeeds
            ConnectionError("Network error"),  # Second call fails
        ]

        strategy = OffsetPaginationStrategy(mock_client, "people", {"limit": 1})

        # Should handle exception and not crash
        with pytest.raises(ConnectionError):
            list(strategy.paginate())

    def test_pond_filter_paginator_handles_verification_errors(self):
        """Test PondFilterPaginator handles verification errors gracefully."""
        mock_client = Mock()

        paginator = PondFilterPaginator(mock_client, 134)

        # Test with malformed person data
        malformed_people = [
            {"id": 1},  # No ponds field
            {"id": 2, "ponds": None},  # Null ponds
            {"id": 3, "ponds": "invalid"},  # Invalid ponds format
        ]

        # Should not crash, should return False
        result = paginator._verify_pond_results(malformed_people)
        assert result is False
