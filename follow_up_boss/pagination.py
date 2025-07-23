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
    """Enhanced NextLink URL-based pagination strategy for deep pagination bypass."""

    def paginate(self) -> Generator[Dict[str, Any], None, None]:
        """
        Paginate using nextLink URLs to bypass deep pagination limits.

        Yields:
            Dictionary containing API response data.
        """
        params = self.params.copy()
        # Optimize for nextLink detection by using smaller initial requests
        if "limit" not in params:
            params["limit"] = 50

        request_count = 0
        max_requests = 1000  # Safety limit to prevent infinite loops

        while request_count < max_requests:
            try:
                logger.debug(
                    f"NextLink request #{request_count + 1} with params: {params}"
                )
                response = self.client._get(self.endpoint, params=params)
                yield response

                request_count += 1

                # Extract nextLink from response
                next_link = self._extract_next_link(response)

                if not next_link:
                    # Check if this is truly the end of data
                    items_key = self._get_items_key(response)
                    if items_key:
                        items_count = len(response.get(items_key, []))
                        logger.debug(f"No nextLink found, received {items_count} items")
                        if items_count < params.get("limit", 50):
                            logger.info(
                                "Reached end of data (fewer items than requested)"
                            )
                            break
                    else:
                        logger.info("No items found in response, ending pagination")
                        break

                    # Try to continue with offset if no nextLink but we have a full page
                    current_offset = params.get("offset", 0)
                    if items_count == params.get("limit", 50):
                        logger.info(
                            "Full page received but no nextLink, trying offset increment"
                        )
                        params["offset"] = current_offset + items_count
                        continue
                    else:
                        break

                # Parse nextLink and update parameters
                logger.info(f"Following nextLink: {next_link}")
                new_params = self._parse_next_link(next_link)

                # Preserve original non-pagination parameters
                for key, value in self.params.items():
                    if key not in ["offset", "limit", "page"]:
                        new_params[key] = value

                params = new_params

            except Exception as e:
                if "Deep pagination disabled" in str(e):
                    logger.warning(
                        f"Deep pagination limit reached at request #{request_count}, nextLink strategy failed"
                    )
                elif "rate limit" in str(e).lower():
                    logger.warning("Rate limit hit, waiting before retry...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"NextLink strategy failed: {e}")
                    raise

        if request_count >= max_requests:
            logger.warning(
                f"NextLink strategy hit maximum request limit ({max_requests})"
            )

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
        next_link = (
            metadata.get("nextLink")
            or metadata.get("next")
            or response.get("nextLink")
            or response.get("next")
        )

        if next_link:
            logger.debug(f"Found nextLink: {next_link}")

        return next_link

    def _parse_next_link(self, next_link: str) -> Dict[str, Any]:
        """
        Parse nextLink URL to extract parameters.

        Args:
            next_link: NextLink URL string.

        Returns:
            Dictionary of parameters extracted from the URL.
        """
        from urllib.parse import parse_qs, urlparse

        try:
            parsed = urlparse(next_link)
            params = parse_qs(parsed.query)

            # Convert single-item lists to strings and handle type conversion
            result: Dict[str, Any] = {}
            for k, v in params.items():
                if len(v) == 1:
                    # Try to convert to appropriate type
                    value = v[0]
                    if k in ["offset", "limit"] and value.isdigit():
                        result[k] = int(value)
                    else:
                        result[k] = value
                else:
                    result[k] = v

            logger.debug(f"Parsed nextLink params: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to parse nextLink URL: {next_link}, error: {e}")
            return {}


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
        # Prioritize NextLink strategy for deep pagination bypass
        self.strategies = [
            NextLinkStrategy,
            OffsetPaginationStrategy,
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
    CRITICAL FIX: Specialized paginator for extracting people from specific ponds.

    This is a complete rewrite to fix the pond filtering regression that was returning
    0 results instead of 334+ leads from pond 134.
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

        # Store original params without pond for fallback
        self.original_params = params.copy()

        # Try using pond parameter in API call first
        params["pond"] = pond_id

        super().__init__(client, "people", params)

    def paginate_all(self) -> List[Dict[str, Any]]:
        """
        CRITICAL FIX: Extract all people from the specified pond using multiple strategies.

        This method fixes the regression by:
        1. Testing if pond parameter actually works with a small sample
        2. Using intelligent verification of results
        3. Falling back to local filtering if API filtering fails
        4. Ensuring we get complete data coverage

        Returns:
            List of all people in the pond.
        """
        logger.info(f"🚀 Starting ENHANCED pond {self.pond_id} extraction...")

        # STRATEGY 1: Test if pond parameter works with a small sample
        test_results = self._test_pond_parameter()

        if test_results["works"]:
            logger.info(f"✅ Pond parameter works! Proceeding with API filtering")
            try:
                # Use API filtering with enhanced pagination strategies
                results = super().paginate_all()

                # Verify results are actually from the pond
                if self._verify_pond_results(results, strict=False):
                    logger.info(
                        f"✅ API filtering successful: {len(results)} people verified from pond {self.pond_id}"
                    )
                    return results
                else:
                    logger.warning(
                        f"⚠️ API filtering returned {len(results)} but verification failed"
                    )
            except Exception as e:
                logger.warning(f"API filtering strategy failed: {e}")

        # STRATEGY 2: Local filtering fallback
        logger.info(f"🔄 Using local filtering fallback for pond {self.pond_id}")
        local_results = self._fetch_and_filter_locally()

        if local_results:
            logger.info(
                f"✅ Local filtering successful: {len(local_results)} people from pond {self.pond_id}"
            )
            return local_results

        # STRATEGY 3: Sample-based extraction and extrapolation
        logger.warning(f"⚠️ All standard methods failed, trying sample-based approach")
        sample_results = self._extract_via_sampling()

        logger.info(
            f"🏁 Pond {self.pond_id} extraction complete: {len(sample_results)} people found"
        )
        return sample_results

    def _test_pond_parameter(self) -> Dict[str, Any]:
        """
        Test if the pond parameter actually works by requesting a small sample.

        Returns:
            Dictionary with test results.
        """
        logger.info(f"🧪 Testing pond {self.pond_id} parameter with small sample...")

        test_result: Dict[str, Any] = {
            "works": False,
            "sample_size": 0,
            "pond_match_count": 0,
            "error": None,
        }

        try:
            # Request a small sample to test pond parameter
            test_params = {"pond": self.pond_id, "limit": 10}
            response = self.client._get("people", params=test_params)

            people = response.get("people", [])
            test_result["sample_size"] = len(people)

            if not people:
                logger.info(
                    "❓ Pond parameter returned 0 results - could be empty pond or broken parameter"
                )
                return test_result

            # Check if returned people are actually in the pond
            pond_match_count = 0
            for person in people:
                if self._person_in_pond(person, self.pond_id):
                    pond_match_count += 1

            test_result["pond_match_count"] = pond_match_count
            test_result["works"] = (
                pond_match_count / len(people)
            ) >= 0.5  # 50% threshold

            logger.info(
                f"🧪 Pond parameter test: {pond_match_count}/{len(people)} people in correct pond "
                f"({'✅ WORKING' if test_result['works'] else '❌ BROKEN'})"
            )

        except Exception as e:
            logger.error(f"❌ Pond parameter test failed: {e}")
            test_result["error"] = str(e)

        return test_result

    def _verify_pond_results(
        self, results: List[Dict[str, Any]], strict: bool = True
    ) -> bool:
        """
        Verify that results actually contain people from the specified pond.

        Args:
            results: List of people returned by the API.
            strict: If True, require high accuracy. If False, be more lenient.

        Returns:
            True if verification passes, False otherwise.
        """
        if not results:
            logger.info("ℹ️ Empty results - could be valid if pond is actually empty")
            return not strict  # In non-strict mode, allow empty results

        verified_count = 0
        total_checked = min(len(results), 50)  # Check up to 50 people for verification

        for person in results[:total_checked]:
            if self._person_in_pond(person, self.pond_id):
                verified_count += 1

        verification_ratio = verified_count / total_checked if total_checked > 0 else 0
        threshold = 0.9 if strict else 0.5  # 90% for strict, 50% for lenient

        logger.info(
            f"🔍 Pond verification: {verified_count}/{total_checked} people verified "
            f"({verification_ratio:.1%}, threshold: {threshold:.0%})"
        )

        return verification_ratio >= threshold

    def _fetch_and_filter_locally(self) -> List[Dict[str, Any]]:
        """
        ENHANCED: Fetch all people and filter by pond locally with optimized strategies.

        Returns:
            List of people filtered by pond.
        """
        logger.info(f"🔄 Starting enhanced local filtering for pond {self.pond_id}")

        # Use original params without pond parameter
        all_people_paginator = SmartPaginator(
            self.client, "people", self.original_params
        )

        try:
            # Use enhanced pagination to get all people
            all_people = all_people_paginator.paginate_all()
            logger.info(
                f"📥 Retrieved {len(all_people)} total people for local filtering"
            )

        except Exception as e:
            logger.error(f"❌ Failed to fetch all people for local filtering: {e}")
            return []

        # Filter by pond locally with progress tracking
        filtered_people = []
        processed_count = 0

        logger.info(f"🔍 Filtering {len(all_people)} people for pond {self.pond_id}...")

        for person in all_people:
            processed_count += 1

            if self._person_in_pond(person, self.pond_id):
                filtered_people.append(person)

            # Progress logging every 1000 people
            if processed_count % 1000 == 0:
                logger.info(
                    f"🔍 Progress: {processed_count}/{len(all_people)} processed, "
                    f"{len(filtered_people)} matches found"
                )

        match_percentage = (
            (len(filtered_people) / len(all_people) * 100) if all_people else 0
        )

        logger.info(
            f"✅ Local filtering complete: {len(filtered_people)} people found in pond {self.pond_id} "
            f"from {len(all_people)} total people ({match_percentage:.2f}%)"
        )

        return filtered_people

    def _extract_via_sampling(self) -> List[Dict[str, Any]]:
        """
        Extract pond data using sampling techniques when other methods fail.

        Returns:
            List of people found through sampling.
        """
        logger.info(f"🎯 Attempting sample-based extraction for pond {self.pond_id}")

        try:
            # Try different sampling approaches
            sample_params = {"pond": self.pond_id, "limit": 100}
            response = self.client._get("people", params=sample_params)
            people = response.get("people", [])

            if people:
                logger.info(f"🎯 Sample extraction found {len(people)} people")

                # Verify these are actually from the pond
                verified_people = []
                for person in people:
                    if self._person_in_pond(person, self.pond_id):
                        verified_people.append(person)

                logger.info(f"🎯 Verified {len(verified_people)} people from sample")
                return verified_people

        except Exception as e:
            logger.error(f"❌ Sample extraction failed: {e}")

        return []

    def _person_in_pond(self, person: Dict[str, Any], pond_id: int) -> bool:
        """
        ENHANCED: Check if a person belongs to the specified pond with better handling.

        Args:
            person: Person data dictionary.
            pond_id: ID of the pond to check.

        Returns:
            True if person is in the pond, False otherwise.
        """
        ponds = person.get("ponds", [])

        # Handle different pond data structures
        if isinstance(ponds, list):
            for pond in ponds:
                if isinstance(pond, dict):
                    if pond.get("id") == pond_id:
                        return True
                elif isinstance(pond, (int, str)):
                    if int(pond) == pond_id:
                        return True
        elif isinstance(ponds, dict):
            if ponds.get("id") == pond_id:
                return True
        elif isinstance(ponds, (int, str)):
            if int(ponds) == pond_id:
                return True

        return False
