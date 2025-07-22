"""
Smart pagination utilities for Follow Up Boss API.

This module provides advanced pagination strategies to handle deep pagination limits,
nextLink URLs, and alternative pagination methods.
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generator, List, Optional, Union

logger = logging.getLogger(__name__)


class PaginationStrategy:
    """Base class for pagination strategies."""

    def __init__(
        self, client: Any, endpoint: str, params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize pagination strategy.

        Args:
            client: The API client instance.
            endpoint: The API endpoint to paginate.
            params: Additional parameters for the API call.
        """
        self.client = client
        self.endpoint = endpoint
        self.params = params or {}
        self.offset_limit = 2000  # FUB API deep pagination limit

    def paginate(self) -> Generator[Dict[str, Any], None, None]:
        """Generate paginated results."""
        raise NotImplementedError("Subclasses must implement paginate method")


class OffsetPaginationStrategy(PaginationStrategy):
    """Standard offset-based pagination strategy."""

    def paginate(self) -> Generator[Dict[str, Any], None, None]:
        """
        Paginate using offset-based pagination.

        Yields:
            Dictionary containing API response data.

        Raises:
            StopIteration: When deep pagination limit is reached.
        """
        offset = self.params.get("offset", 0)
        limit = self.params.get("limit", 100)

        while True:
            current_params = {**self.params, "offset": offset, "limit": limit}

            try:
                response = self.client._get(self.endpoint, params=current_params)
                yield response

                # Check if we got fewer results than requested (end of data)
                items_key = self._get_items_key(response)
                if items_key and len(response.get(items_key, [])) < limit:
                    break

                offset += limit

                # Check if we're approaching the deep pagination limit
                if offset >= self.offset_limit:
                    logger.warning(
                        f"Approaching deep pagination limit at offset {offset}"
                    )
                    break

            except Exception as e:
                if "Deep pagination disabled" in str(e):
                    logger.warning(f"Deep pagination limit reached at offset {offset}")
                    break
                raise

    def _get_items_key(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Determine the key containing the list of items in the response.

        Args:
            response: API response dictionary.

        Returns:
            Key name containing the list of items, or None if not found.
        """
        # Common patterns in FUB API responses
        for key in ["people", "deals", "events", "notes", "calls", "tasks"]:
            if key in response and isinstance(response[key], list):
                return key
        return None


class DateRangeStrategy(PaginationStrategy):
    """Date-range based pagination strategy."""

    def __init__(
        self,
        client: Any,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        date_field: str = "created",
        chunk_days: int = 30,
    ):
        """
        Initialize date-range pagination strategy.

        Args:
            client: The API client instance.
            endpoint: The API endpoint to paginate.
            params: Additional parameters for the API call.
            date_field: Date field to use for chunking ('created' or 'updated').
            chunk_days: Number of days per chunk.
        """
        super().__init__(client, endpoint, params)
        self.date_field = date_field
        self.chunk_days = chunk_days

    def paginate(self) -> Generator[Dict[str, Any], None, None]:
        """
        Paginate using date range chunks.

        Yields:
            Dictionary containing API response data.
        """
        # Determine date range
        end_date = datetime.now()
        start_date = self.params.get("start_date")

        if not start_date:
            # Default to 2 years ago if no start date specified
            start_date = end_date - timedelta(days=730)
        elif isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

        current_date = start_date

        while current_date < end_date:
            chunk_end = min(current_date + timedelta(days=self.chunk_days), end_date)

            # Create date-specific parameters
            date_params = {**self.params}
            date_params[f"{self.date_field}_start"] = current_date.isoformat()
            date_params[f"{self.date_field}_end"] = chunk_end.isoformat()

            logger.info(
                f"Fetching data from {current_date.date()} to {chunk_end.date()}"
            )

            # Use offset pagination within this date range
            offset_strategy = OffsetPaginationStrategy(
                self.client, self.endpoint, date_params
            )

            for response in offset_strategy.paginate():
                yield response

            current_date = chunk_end


class NextLinkStrategy(PaginationStrategy):
    """NextLink URL-based pagination strategy."""

    def paginate(self) -> Generator[Dict[str, Any], None, None]:
        """
        Paginate using nextLink URLs when available.

        Yields:
            Dictionary containing API response data.
        """
        params = self.params.copy()

        while True:
            response = self.client._get(self.endpoint, params=params)
            yield response

            # Check for nextLink in response
            next_link = self._extract_next_link(response)
            if not next_link:
                break

            # Parse nextLink URL to extract new parameters
            params = self._parse_next_link(next_link)

    def _extract_next_link(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Extract nextLink URL from API response.

        Args:
            response: API response dictionary.

        Returns:
            NextLink URL if found, None otherwise.
        """
        # Check common locations for nextLink
        metadata = response.get("_metadata", {})
        return (
            metadata.get("nextLink") or metadata.get("next") or response.get("nextLink")
        )

    def _parse_next_link(self, next_link: str) -> Dict[str, Any]:
        """
        Parse nextLink URL to extract parameters.

        Args:
            next_link: NextLink URL string.

        Returns:
            Dictionary of parameters extracted from the URL.
        """
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(next_link)
        params = parse_qs(parsed.query)

        # Convert single-item lists to strings
        return {k: v[0] if len(v) == 1 else v for k, v in params.items()}


class SmartPaginator:
    """
    Intelligent paginator that automatically selects the best strategy.

    This class tries multiple pagination strategies to ensure complete data extraction
    even when hitting API limits.
    """

    def __init__(
        self, client: Any, endpoint: str, params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize smart paginator.

        Args:
            client: The API client instance.
            endpoint: The API endpoint to paginate.
            params: Additional parameters for the API call.
        """
        self.client = client
        self.endpoint = endpoint
        self.params = params or {}
        self.offset_limit = 2000  # FUB API deep pagination limit
        self.strategies = [
            OffsetPaginationStrategy,
            NextLinkStrategy,
            DateRangeStrategy,
        ]

    def paginate_all(self) -> List[Dict[str, Any]]:
        """
        Extract all data using the most appropriate pagination strategy.

        Returns:
            List of all items extracted from the API.

        Raises:
            RuntimeError: If all pagination strategies fail.
        """
        all_items = []
        seen_ids = set()

        for strategy_class in self.strategies:
            try:
                logger.info(f"Trying pagination strategy: {strategy_class.__name__}")
                strategy = strategy_class(self.client, self.endpoint, self.params)

                for response in strategy.paginate():
                    items = self._extract_items(response)

                    # Deduplicate items
                    new_items = []
                    for item in items:
                        item_id = item.get("id")
                        if item_id and item_id not in seen_ids:
                            seen_ids.add(item_id)
                            new_items.append(item)

                    all_items.extend(new_items)
                    logger.info(
                        f"Extracted {len(new_items)} new items, total: {len(all_items)}"
                    )

                # If we got data with this strategy, return it
                if all_items:
                    logger.info(
                        f"Successfully extracted {len(all_items)} items using {strategy_class.__name__}"
                    )
                    return all_items

            except Exception as e:
                logger.warning(f"Strategy {strategy_class.__name__} failed: {e}")
                continue

        if not all_items:
            raise RuntimeError("All pagination strategies failed to extract data")

        return all_items

    def paginate_concurrent(self, max_workers: int = 5) -> List[Dict[str, Any]]:
        """
        Extract data using concurrent requests for improved performance.

        Args:
            max_workers: Maximum number of concurrent workers.

        Returns:
            List of all items extracted from the API.
        """
        all_items = []
        seen_ids = set()
        lock = threading.Lock()

        def fetch_chunk(offset: int, limit: int) -> List[Dict[str, Any]]:
            """Fetch a chunk of data with the given offset and limit."""
            try:
                params = {**self.params, "offset": offset, "limit": limit}
                response = self.client._get(self.endpoint, params=params)
                return self._extract_items(response)
            except Exception as e:
                logger.warning(f"Failed to fetch chunk at offset {offset}: {e}")
                return []

        # First, determine the total number of items if possible
        initial_response = self.client._get(
            self.endpoint, params={**self.params, "limit": 1}
        )
        total_items = self._get_total_count(initial_response)

        if total_items and total_items <= self.offset_limit:
            # Use concurrent requests for data within the offset limit
            chunk_size = 100
            offsets = range(0, min(total_items, self.offset_limit), chunk_size)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_offset = {
                    executor.submit(fetch_chunk, offset, chunk_size): offset
                    for offset in offsets
                }

                for future in as_completed(future_to_offset):
                    items = future.result()

                    with lock:
                        for item in items:
                            item_id = item.get("id")
                            if item_id and item_id not in seen_ids:
                                seen_ids.add(item_id)
                                all_items.append(item)
        else:
            # Fall back to sequential smart pagination
            return self.paginate_all()

        return all_items

    def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract items from API response.

        Args:
            response: API response dictionary.

        Returns:
            List of items from the response.
        """
        # Common patterns in FUB API responses
        for key in ["people", "deals", "events", "notes", "calls", "tasks"]:
            if key in response and isinstance(response[key], list):
                return list(response[key])  # Ensure correct return type

        # If no known key found, return empty list
        return []

    def _get_total_count(self, response: Dict[str, Any]) -> Optional[int]:
        """
        Extract total count from API response metadata.

        Args:
            response: API response dictionary.

        Returns:
            Total count if available, None otherwise.
        """
        metadata = response.get("_metadata", {})
        total = metadata.get("total") or metadata.get("totalCount")
        return int(total) if total is not None else None


class PondFilterPaginator(SmartPaginator):
    """
    Specialized paginator for extracting people from specific ponds.

    Handles the broken pond filtering by implementing multiple strategies.
    """

    def __init__(
        self, client: Any, pond_id: int, params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize pond filter paginator.

        Args:
            client: The API client instance.
            pond_id: ID of the pond to filter by.
            params: Additional parameters for the API call.
        """
        self.pond_id = pond_id
        params = params or {}

        # Try using pond parameter in API call first
        params["pond"] = pond_id

        super().__init__(client, "people", params)

    def paginate_all(self) -> List[Dict[str, Any]]:
        """
        Extract all people from the specified pond.

        Returns:
            List of all people in the pond.
        """
        # First try with pond parameter
        try:
            results = super().paginate_all()

            # Verify that pond filtering actually worked
            if self._verify_pond_filtering(results):
                return results
            else:
                logger.warning(
                    "Pond parameter filtering failed, falling back to post-fetch filtering"
                )
        except Exception as e:
            logger.warning(f"Pond parameter strategy failed: {e}")

        # Fall back to fetching all people and filtering locally
        return self._fetch_and_filter_all()

    def _verify_pond_filtering(self, results: List[Dict[str, Any]]) -> bool:
        """
        Verify that the API actually filtered by pond.

        Args:
            results: List of people returned by the API.

        Returns:
            True if pond filtering worked, False otherwise.
        """
        if not results:
            return True  # Empty results could be valid

        # Check if all returned people are in the specified pond
        for person in results[:10]:  # Check first 10 people
            ponds = person.get("ponds", [])
            if isinstance(ponds, list):
                pond_ids = [p.get("id") if isinstance(p, dict) else p for p in ponds]
                if self.pond_id not in pond_ids:
                    return False
            elif isinstance(ponds, dict) and ponds.get("id") != self.pond_id:
                return False

        return True

    def _fetch_and_filter_all(self) -> List[Dict[str, Any]]:
        """
        Fetch all people and filter by pond locally.

        Returns:
            List of people filtered by pond.
        """
        # Remove pond parameter and fetch all people
        params_without_pond = {k: v for k, v in self.params.items() if k != "pond"}
        all_people_paginator = SmartPaginator(
            self.client, "people", params_without_pond
        )

        all_people = all_people_paginator.paginate_all()

        # Filter by pond locally
        filtered_people = []
        for person in all_people:
            if self._person_in_pond(person, self.pond_id):
                filtered_people.append(person)

        logger.info(
            f"Filtered {len(filtered_people)} people from {len(all_people)} total people for pond {self.pond_id}"
        )
        return filtered_people

    def _person_in_pond(self, person: Dict[str, Any], pond_id: int) -> bool:
        """
        Check if a person belongs to the specified pond.

        Args:
            person: Person data dictionary.
            pond_id: ID of the pond to check.

        Returns:
            True if person is in the pond, False otherwise.
        """
        ponds = person.get("ponds", [])

        if isinstance(ponds, list):
            for pond in ponds:
                if isinstance(pond, dict) and pond.get("id") == pond_id:
                    return True
                elif isinstance(pond, int) and pond == pond_id:
                    return True
        elif isinstance(ponds, dict) and ponds.get("id") == pond_id:
            return True
        elif isinstance(ponds, int) and ponds == pond_id:
            return True

        return False
