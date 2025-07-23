"""
Test cases for critical issues requiring immediate fixes:
1. Pond filtering regression (0 results instead of 334+ leads)
2. Deep pagination limit (2000 offset limit)
3. Enhanced methods implementation
"""

from typing import Any, Optional
from unittest.mock import Mock, patch

import pytest

from follow_up_boss.enhanced_client import RobustApiClient
from follow_up_boss.enhanced_people import EnhancedPeople
from follow_up_boss.pagination import PondFilterPaginator, SmartPaginator


@pytest.mark.integration
class TestCriticalPondFiltering:
    """Test cases for pond filtering regression fixes."""

    def test_pond_134_extraction_should_return_334_leads(
        self, robust_client: Optional[RobustApiClient]
    ) -> None:
        """
        Test that pond 134 extraction returns expected 334+ leads.
        This test reproduces the critical pond filtering regression.
        """
        if not robust_client:
            pytest.skip("No API credentials available for integration test")

        enhanced_people = EnhancedPeople(robust_client)

        # Test 1: Sample extraction to verify API connectivity
        sample = enhanced_people.extract_pond_sample(134, 10)
        assert (
            len(sample) > 0
        ), "Pond 134 sample extraction should return at least some results"

        # Verify sample people actually belong to pond 134
        for person in sample:
            ponds = person.get("ponds", [])
            pond_ids = []
            if isinstance(ponds, list):
                pond_ids = [p.get("id") if isinstance(p, dict) else p for p in ponds]
            elif isinstance(ponds, dict):
                pond_ids = [ponds.get("id")]
            assert (
                134 in pond_ids
            ), f"Person {person.get('id')} should belong to pond 134"

        # Test 2: Full pond extraction
        pond_people = enhanced_people.get_by_pond(134)

        # Critical assertion: Should return 334+ leads, not 0
        assert (
            len(pond_people) >= 334
        ), f"Pond 134 should return at least 334 leads, got {len(pond_people)}"

        # Verify all returned people actually belong to pond 134
        verified_count = 0
        for person in pond_people[:10]:  # Check first 10
            ponds = person.get("ponds", [])
            if isinstance(ponds, list):
                pond_ids = [p.get("id") if isinstance(p, dict) else p for p in ponds]
                if 134 in pond_ids:
                    verified_count += 1

        assert (
            verified_count > 0
        ), "At least some people should be verified as belonging to pond 134"

    def test_pond_filtering_api_parameter_vs_local_filtering(
        self, robust_client: Optional[RobustApiClient]
    ) -> None:
        """
        Test that pond filtering works whether API parameter works or not.
        This ensures the fallback mechanism works correctly.
        """
        if not robust_client:
            pytest.skip("No API credentials available for integration test")

        enhanced_people = EnhancedPeople(robust_client)

        # Test pond parameter filtering
        pond_people_api = enhanced_people.get_by_pond(134)

        # If API filtering fails, the system should fall back to local filtering
        # and still return correct results
        assert (
            len(pond_people_api) > 0
        ), "Pond filtering should return results via API or local fallback"


@pytest.mark.integration
class TestDeepPaginationBypass:
    """Test cases for deep pagination limit bypass."""

    def test_extract_beyond_2000_offset_limit(
        self, robust_client: Optional[RobustApiClient]
    ) -> None:
        """
        Test that the system can extract data beyond the 2000 offset limit.
        This addresses the "Deep pagination disabled" error.
        """
        if not robust_client:
            pytest.skip("No API credentials available for integration test")

        enhanced_people = EnhancedPeople(robust_client)

        # Test extracting all people (should be 50,000+ total)
        # This should not fail at 2000 offset
        all_people = enhanced_people.get_all(
            limit=100
        )  # Use smaller chunks for efficiency

        # Should be able to extract more than 2000 records
        assert (
            len(all_people) > 2000
        ), f"Should extract more than 2000 people, got {len(all_people)}"

        # Test specific pond that has 11,627+ leads
        pond_134_people = enhanced_people.get_by_pond(134)

        # Should extract all 11,627+ leads from pond 134
        assert (
            len(pond_134_people) > 2000
        ), f"Pond 134 should have more than 2000 people, got {len(pond_134_people)}"

    def test_nextlink_pagination_strategy(
        self, robust_client: Optional[RobustApiClient]
    ) -> None:
        """
        Test that nextLink pagination strategy works for deep pagination.
        """
        if not robust_client:
            pytest.skip("No API credentials available for integration test")

        # Test SmartPaginator with nextLink strategy
        paginator = SmartPaginator(robust_client, "people", {"limit": 100})

        # Should be able to paginate beyond 2000 offset using nextLink
        all_people = paginator.paginate_all()
        assert (
            len(all_people) > 2000
        ), "NextLink pagination should bypass 2000 offset limit"


@pytest.mark.unit
class TestEnhancedMethodsImplementation:
    """Test cases for enhanced methods that should be available."""

    def test_enhanced_people_has_required_methods(
        self, mock_robust_client: Mock
    ) -> None:
        """
        Test that all required enhanced methods are implemented.
        """
        enhanced_people = EnhancedPeople(mock_robust_client)

        # Critical enhanced methods
        required_methods = [
            "get_all",
            "get_by_pond",
            "get_pond_members_comprehensive",
            "get_concurrent",
            "get_with_progress",
            "extract_pond_sample",
            "verify_pond_extraction",
            "get_extraction_stats",
            "export_to_csv",
            "export_to_json",
        ]

        for method_name in required_methods:
            assert hasattr(
                enhanced_people, method_name
            ), f"EnhancedPeople should have {method_name} method"
            assert callable(
                getattr(enhanced_people, method_name)
            ), f"{method_name} should be callable"

    def test_pond_filter_paginator_has_correct_implementation(
        self, mock_robust_client: Mock
    ) -> None:
        """
        Test that PondFilterPaginator correctly implements pond filtering.
        """
        pond_paginator = PondFilterPaginator(mock_robust_client, 134, {"limit": 100})

        # Should have pond_id set
        assert pond_paginator.pond_id == 134

        # Should have pond parameter in params
        assert pond_paginator.params.get("pond") == 134

        # Should have methods for verification and fallback
        assert hasattr(pond_paginator, "_verify_pond_filtering")
        assert hasattr(pond_paginator, "_fetch_and_filter_all")
        assert hasattr(pond_paginator, "_person_in_pond")


@pytest.mark.integration
class TestComprehensivePondExtractionWorkaround:
    """
    Comprehensive test that validates the complete pond extraction workflow.
    """

    def test_pond_134_complete_extraction_workflow(
        self, robust_client: Optional[RobustApiClient]
    ) -> None:
        """
        Test the complete workflow for extracting all 11,627+ leads from pond 134.
        This is the critical business requirement.
        """
        if not robust_client:
            pytest.skip("No API credentials available for integration test")

        enhanced_people = EnhancedPeople(robust_client)

        # Step 1: Verify pond exists and has expected data
        verification_result = enhanced_people.verify_pond_extraction(134, 11627)
        assert verification_result[
            "verification_passed"
        ], f"Pond 134 verification failed: {verification_result}"

        # Step 2: Extract all people from pond 134
        pond_people = enhanced_people.get_pond_members_comprehensive(134)

        # Step 3: Validate extraction results
        assert (
            len(pond_people) >= 11627
        ), f"Should extract at least 11,627 leads, got {len(pond_people)}"

        # Step 4: Verify data quality
        assert all(
            "id" in person for person in pond_people
        ), "All people should have IDs"

        # Step 5: Export to validate functionality
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                json_file = enhanced_people.export_to_json(pond_people, tmp.name)
                assert json_file.endswith(".json"), "Should export to JSON successfully"
        except Exception as e:
            pytest.fail(f"Export functionality failed: {e}")


@pytest.mark.unit
class TestMockPondFilteringFix:
    """
    Unit tests with mocks to validate pond filtering fixes.
    """

    @patch("follow_up_boss.pagination.PondFilterPaginator.paginate_all")
    def test_pond_filtering_fix_with_mock(
        self, mock_paginate_all: Mock, mock_robust_client: Mock
    ) -> None:
        """
        Test pond filtering fix using mocks to simulate correct behavior.
        """
        # Mock returning 334 people from pond 134
        mock_pond_people = [
            {
                "id": i,
                "name": f"Person {i}",
                "ponds": [{"id": 134, "name": "Test Pond"}],
            }
            for i in range(1, 335)  # 334 people
        ]

        mock_paginate_all.return_value = mock_pond_people

        enhanced_people = EnhancedPeople(mock_robust_client)
        result = enhanced_people.get_by_pond(134)

        # Should return 334 people, not 0
        assert len(result) == 334, f"Should return 334 people, got {len(result)}"

        # All people should belong to pond 134
        for person in result:
            ponds = person.get("ponds", [])
            pond_ids = [p.get("id") for p in ponds if isinstance(p, dict)]
            assert 134 in pond_ids, f"Person {person['id']} should belong to pond 134"
