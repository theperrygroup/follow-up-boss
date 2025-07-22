"""
Enhanced People API with advanced pagination and filtering capabilities.

This module provides enhanced methods for extracting people data from Follow Up Boss,
including deep pagination bypass, reliable pond filtering, and comprehensive data operations.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .enhanced_client import RobustApiClient
from .pagination import PondFilterPaginator, SmartPaginator
from .people import People

logger = logging.getLogger(__name__)


class EnhancedPeople(People):
    """
    Enhanced People API client with advanced pagination and filtering capabilities.

    Features:
    - Deep pagination bypass (beyond 2000 offset limit)
    - Reliable pond filtering
    - Concurrent data extraction
    - Progress tracking and logging
    - Automatic retry and recovery
    """

    def __init__(self, client: Union[RobustApiClient, Any]):
        """
        Initialize the enhanced People API.

        Args:
            client: An instance of RobustApiClient or FollowUpBossApiClient.
        """
        super().__init__(client)
        self._extraction_stats = {
            "total_requests": 0,
            "total_people_extracted": 0,
            "extraction_time": 0.0,
            "last_extraction": None,
        }

    def get_all(self, **filters: Any) -> List[Dict[str, Any]]:
        """
        Extract ALL people regardless of pagination limits.

        This method automatically handles deep pagination by using multiple strategies:
        1. Standard offset pagination (up to 2000 limit)
        2. Date-range chunking for data beyond limits
        3. Alternative pagination methods as fallbacks

        Args:
            **filters: Additional filters to apply (e.g., tag, stage, etc.)

        Returns:
            List of all people matching the filters.

        Example:
            people = enhanced_people.get_all(limit=100)
            all_people = enhanced_people.get_all()
        """
        start_time = time.time()

        logger.info("Starting comprehensive people extraction...")

        try:
            paginator = SmartPaginator(self._client, "people", filters)
            all_people = paginator.paginate_all()

            extraction_time = time.time() - start_time

            # Update statistics
            self._extraction_stats["total_requests"] = (
                self._extraction_stats.get("total_requests", 0) + 1
            )
            self._extraction_stats["total_people_extracted"] = len(all_people)
            self._extraction_stats["extraction_time"] = extraction_time
            self._extraction_stats["last_extraction"] = datetime.now().isoformat()

            logger.info(
                f"Successfully extracted {len(all_people)} people in {extraction_time:.2f} seconds"
            )

            return all_people

        except Exception as e:
            logger.error(f"Failed to extract all people: {e}")
            raise

    def get_by_pond(self, pond_id: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Reliable pond filtering that actually works.

        This method implements multiple strategies to ensure complete pond data extraction:
        1. Try API pond parameter first
        2. Fall back to post-fetch filtering if API filtering fails
        3. Verify filtering accuracy

        Args:
            pond_id: The ID of the pond to filter by.
            **kwargs: Additional parameters for the API call.

        Returns:
            List of all people in the specified pond.

        Example:
            pond_134_people = enhanced_people.get_by_pond(134)
            pond_people_with_limit = enhanced_people.get_by_pond(134, limit=50)
        """
        start_time = time.time()

        logger.info(f"Starting pond {pond_id} extraction...")

        try:
            paginator = PondFilterPaginator(self._client, pond_id, kwargs)
            pond_people = paginator.paginate_all()

            extraction_time = time.time() - start_time

            logger.info(
                f"Successfully extracted {len(pond_people)} people from pond {pond_id} "
                f"in {extraction_time:.2f} seconds"
            )

            return pond_people

        except Exception as e:
            logger.error(f"Failed to extract people from pond {pond_id}: {e}")
            raise

    def get_pond_members_comprehensive(self, pond_id: int) -> List[Dict[str, Any]]:
        """
        Get ALL members of a pond, regardless of pagination limits.

        This is the most comprehensive method for pond extraction, combining
        multiple strategies for complete data coverage.

        Args:
            pond_id: The ID of the pond to extract.

        Returns:
            List of all people in the pond with complete data coverage.

        Example:
            all_pond_134_people = enhanced_people.get_pond_members_comprehensive(134)
        """
        return self.get_by_pond(pond_id)

    def get_concurrent(self, max_workers: int = 5, **filters) -> List[Dict[str, Any]]:
        """
        Extract people data using concurrent requests for improved performance.

        Args:
            max_workers: Maximum number of concurrent workers.
            **filters: Additional filters to apply.

        Returns:
            List of all people extracted concurrently.

        Example:
            people = enhanced_people.get_concurrent(max_workers=10, limit=50)
        """
        start_time = time.time()

        logger.info(
            f"Starting concurrent people extraction with {max_workers} workers..."
        )

        try:
            paginator = SmartPaginator(self._client, "people", filters)
            all_people = paginator.paginate_concurrent(max_workers=max_workers)

            extraction_time = time.time() - start_time

            logger.info(
                f"Successfully extracted {len(all_people)} people concurrently "
                f"in {extraction_time:.2f} seconds"
            )

            return all_people

        except Exception as e:
            logger.error(f"Failed to extract people concurrently: {e}")
            raise

    def get_with_progress(self, callback=None, **filters) -> List[Dict[str, Any]]:
        """
        Extract people data with progress tracking.

        Args:
            callback: Optional callback function called with progress updates.
                     Signature: callback(current_count, total_estimated, elapsed_time)
            **filters: Additional filters to apply.

        Returns:
            List of all people extracted.

        Example:
            def progress_callback(current, total, elapsed):
                print(f"Progress: {current}/{total} ({elapsed:.1f}s)")

            people = enhanced_people.get_with_progress(
                callback=progress_callback,
                limit=100
            )
        """
        start_time = time.time()
        all_people = []

        logger.info("Starting people extraction with progress tracking...")

        try:
            paginator = SmartPaginator(self._client, "people", filters)

            for strategy_class in paginator.strategies:
                try:
                    strategy = strategy_class(self._client, "people", filters)

                    for response in strategy.paginate():
                        items = paginator._extract_items(response)
                        all_people.extend(items)

                        if callback:
                            elapsed_time = time.time() - start_time
                            callback(len(all_people), None, elapsed_time)

                    # If we got data, break out of strategy loop
                    if all_people:
                        break

                except Exception as e:
                    logger.warning(f"Strategy failed: {e}")
                    continue

            extraction_time = time.time() - start_time

            if callback:
                callback(len(all_people), len(all_people), extraction_time)

            logger.info(
                f"Successfully extracted {len(all_people)} people with progress tracking "
                f"in {extraction_time:.2f} seconds"
            )

            return all_people

        except Exception as e:
            logger.error(f"Failed to extract people with progress tracking: {e}")
            raise

    def extract_pond_sample(
        self, pond_id: int, sample_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Extract a sample of people from a pond for testing purposes.

        Args:
            pond_id: The ID of the pond to sample from.
            sample_size: Number of people to extract.

        Returns:
            List of sample people from the pond.

        Example:
            sample = enhanced_people.extract_pond_sample(134, 50)
        """
        logger.info(f"Extracting sample of {sample_size} people from pond {pond_id}...")

        try:
            params = {"pond": pond_id, "limit": sample_size}
            response = self._client._get("people", params=params)

            people = response.get("people", [])

            logger.info(f"Successfully extracted sample of {len(people)} people")

            return people

        except Exception as e:
            logger.error(f"Failed to extract pond sample: {e}")
            raise

    def verify_pond_extraction(
        self, pond_id: int, expected_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verify the accuracy of pond extraction by comparing different methods.

        Args:
            pond_id: The ID of the pond to verify.
            expected_count: Expected number of people in the pond.

        Returns:
            Dictionary containing verification results.

        Example:
            results = enhanced_people.verify_pond_extraction(134, 11627)
        """
        logger.info(f"Verifying pond {pond_id} extraction accuracy...")

        verification_results = {
            "pond_id": pond_id,
            "expected_count": expected_count,
            "extraction_methods": {},
            "verification_passed": False,
            "recommendation": "",
        }

        try:
            # Method 1: Sample extraction to verify pond parameter works
            sample = self.extract_pond_sample(pond_id, 10)
            verification_results["extraction_methods"]["sample"] = {
                "count": len(sample),
                "works": len(sample) > 0,
            }

            # Method 2: Try comprehensive extraction
            start_time = time.time()
            comprehensive_people = self.get_by_pond(pond_id)
            extraction_time = time.time() - start_time

            verification_results["extraction_methods"]["comprehensive"] = {
                "count": len(comprehensive_people),
                "extraction_time": extraction_time,
                "works": len(comprehensive_people) > 0,
            }

            # Verify pond membership
            verified_count = 0
            for person in comprehensive_people[:10]:  # Check first 10
                ponds = person.get("ponds", [])
                if isinstance(ponds, list):
                    pond_ids = [
                        p.get("id") if isinstance(p, dict) else p for p in ponds
                    ]
                    if pond_id in pond_ids:
                        verified_count += 1
                elif isinstance(ponds, dict) and ponds.get("id") == pond_id:
                    verified_count += 1

            verification_results["pond_membership_verified"] = verified_count > 0

            # Compare with expected count
            if expected_count:
                accuracy = len(comprehensive_people) / expected_count
                verification_results["accuracy"] = accuracy
                verification_results["verification_passed"] = (
                    accuracy > 0.95
                )  # 95% accuracy threshold
            else:
                verification_results["verification_passed"] = (
                    len(comprehensive_people) > 0
                )

            # Recommendations
            if verification_results["verification_passed"]:
                verification_results["recommendation"] = "Extraction working correctly"
            else:
                verification_results["recommendation"] = "Manual investigation required"

            logger.info(f"Pond verification completed: {verification_results}")

            return verification_results

        except Exception as e:
            logger.error(f"Pond verification failed: {e}")
            verification_results["error"] = str(e)
            verification_results[
                "recommendation"
            ] = "Check API connectivity and permissions"
            return verification_results

    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about data extractions performed.

        Returns:
            Dictionary containing extraction statistics.
        """
        return self._extraction_stats.copy()

    def export_to_csv(self, people_data: List[Dict[str, Any]], filename: str) -> str:
        """
        Export people data to CSV format.

        Args:
            people_data: List of people dictionaries to export.
            filename: Name of the CSV file to create.

        Returns:
            Path to the created CSV file.

        Example:
            people = enhanced_people.get_by_pond(134)
            csv_file = enhanced_people.export_to_csv(people, "pond_134_people.csv")
        """
        import csv
        import os

        if not people_data:
            raise ValueError("No people data to export")

        # Get all unique keys from all people records
        all_keys = set()
        for person in people_data:
            all_keys.update(person.keys())

        fieldnames = sorted(list(all_keys))

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for person in people_data:
                # Flatten complex fields for CSV
                flattened_person = {}
                for key, value in person.items():
                    if isinstance(value, (list, dict)):
                        flattened_person[key] = str(value)
                    else:
                        flattened_person[key] = value

                writer.writerow(flattened_person)

        abs_path = os.path.abspath(filename)
        logger.info(f"Exported {len(people_data)} people to {abs_path}")

        return abs_path

    def export_to_json(self, people_data: List[Dict[str, Any]], filename: str) -> str:
        """
        Export people data to JSON format.

        Args:
            people_data: List of people dictionaries to export.
            filename: Name of the JSON file to create.

        Returns:
            Path to the created JSON file.

        Example:
            people = enhanced_people.get_by_pond(134)
            json_file = enhanced_people.export_to_json(people, "pond_134_people.json")
        """
        import json
        import os

        if not people_data:
            raise ValueError("No people data to export")

        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(people_data, jsonfile, indent=2, default=str)

        abs_path = os.path.abspath(filename)
        logger.info(f"Exported {len(people_data)} people to {abs_path}")

        return abs_path


# Convenience functions for quick access
def extract_all_people(client: Optional[Any] = None) -> List[Dict[str, Any]]:
    """
    Quick function to extract all people using enhanced capabilities.

    Args:
        client: Optional API client instance. If None, creates a new RobustApiClient.

    Returns:
        List of all people in the system.
    """
    if client is None:
        client = RobustApiClient()

    enhanced_people = EnhancedPeople(client)
    return enhanced_people.get_all()


def extract_pond_people(
    pond_id: int, client: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Quick function to extract all people from a specific pond.

    Args:
        pond_id: The ID of the pond to extract from.
        client: Optional API client instance. If None, creates a new RobustApiClient.

    Returns:
        List of all people in the specified pond.
    """
    if client is None:
        client = RobustApiClient()

    enhanced_people = EnhancedPeople(client)
    return enhanced_people.get_by_pond(pond_id)


def verify_pond_extraction_quick(
    pond_id: int, expected_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Quick function to verify pond extraction accuracy.

    Args:
        pond_id: The ID of the pond to verify.
        expected_count: Expected number of people in the pond.

    Returns:
        Dictionary containing verification results.
    """
    client = RobustApiClient()
    enhanced_people = EnhancedPeople(client)
    return enhanced_people.verify_pond_extraction(pond_id, expected_count)
