"""
API bindings for Follow Up Boss People endpoints.
"""

import logging
from typing import Any, Dict, Iterator, List, Optional, TypedDict, Union, cast

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class ListPeopleParams(TypedDict, total=False):
    """Query parameters for listing people.

    Attributes:
        limit: Page size.
        offset: Offset for offset-based pagination.
        sort: Sort expression supported by API.
        fields: Comma-separated field list to include in responses.
        stage: Stage filter.
        tag: Tag filter.
        listId: Saved List ID filter (enables cursor pagination via `_metadata.next`).
        next: Cursor token for subsequent page requests.
    """

    limit: int
    offset: int
    sort: str
    fields: str
    stage: Union[str, int]
    tag: str
    listId: int
    next: str


class Person(TypedDict, total=False):
    """A minimal person representation.

    Only ``id`` is guaranteed; other keys are provided by the API and may vary.
    """

    id: int


class PeopleListResponse(TypedDict, total=False):
    """Standardized shape for people list responses."""

    people: List[Person]
    count: int
    _metadata: Dict[str, Any]


class People:
    """
    Provides access to the People endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the People resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_people(
        self, params: Optional[ListPeopleParams] = None
    ) -> PeopleListResponse:
        """
        Retrieves a list of people.

        This method accepts and forwards saved list filters via ``listId``.
        When ``listId`` is used, the API may return a cursor token in
        ``_metadata.next`` for pagination.

        Args:
            params: Optional query parameters to filter the results
                (e.g., ``limit``, ``offset``, ``sort``, ``fields``, ``stage``, ``tag``, ``listId``).

        Returns:
            A standardized dictionary containing at least ``people`` (list) and
            ``count`` (int) along with any other fields provided by the API, such as
            ``_metadata``. If available, ``_metadata.nextLink`` and ``_metadata.total``
            are included.
        """
        response: Dict[str, Any] = self._client._get(
            "people", params=cast(Optional[Dict[str, Any]], params)
        )
        # Ensure consistent shape
        people_list: List[Person] = []
        if isinstance(response, dict):
            raw_people = response.get("people", [])
            if isinstance(raw_people, list):
                people_list = cast(List[Person], raw_people)
            response.setdefault("people", people_list)
            response.setdefault("count", len(people_list))
            # Ensure concise metadata
            meta: Dict[str, Any] = cast(Dict[str, Any], response.get("_metadata", {}))
            response.setdefault("_metadata", meta)
            if "limit" not in meta and params and "limit" in params:
                meta["limit"] = params["limit"]
            if "listId" not in meta and params and "listId" in params:
                meta["listId"] = params["listId"]
        return cast(PeopleListResponse, response)

    def create_person(self, person_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Creates a new person.

        Args:
            person_data: A dictionary containing the details of the person to create.

        Returns:
            A dictionary containing the details of the newly created person or an error string.
        """
        return self._client._post("people", json_data=person_data)

    def retrieve_person(
        self, person_id: int, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a specific person by their ID.

        Args:
            person_id: The ID of the person to retrieve.
            params: Optional query parameters (e.g., fields="id,name,emails").

        Returns:
            A dictionary containing the details of the person.
        """
        return self._client._get(f"people/{person_id}", params=params)

    def update_person(
        self, person_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing person.

        Args:
            person_id: The ID of the person to update.
            update_data: A dictionary containing the fields to update.

        Returns:
            A dictionary containing the details of the updated person or an error string.
        """
        return self._client._put(f"people/{person_id}", json_data=update_data)

    def delete_person(self, person_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific person by their ID.

        Args:
            person_id: The ID of the person to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self._client._delete(f"people/{person_id}")

    def check_duplicate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks for duplicate people based on provided criteria (e.g., email, phone).
        At least one identifier (email, phone) must be in params.

        Args:
            params: Query parameters (e.g., {"email": "test@example.com"}).

        Returns:
            A dictionary containing the API response.

        Raises:
            ValueError: If params is empty or missing key identifiers.
        """
        if not params or not any(key in params for key in ["email", "phone"]):
            raise ValueError(
                "Params must include at least 'email' or 'phone' to check for duplicates."
            )
        return self._client._get("people/checkDuplicate", params=params)

    def list_unclaimed_people(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of unclaimed people.

        Args:
            params: Optional query parameters (e.g., limit, offset).

        Returns:
            A dictionary containing the list of unclaimed people and pagination information.
        """
        return self._client._get("people/unclaimed", params=params)

    def claim_person(self, payload: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Claims an unclaimed person, assigning them to a user.

        Args:
            payload: Dictionary for the request body, typically including `personId`
                     and optionally `userId`.

        Returns:
            A dictionary containing the API response or an error string.
        """
        return self._client._post("people/claim", json_data=payload)

    def ignore_unclaimed_person(
        self, payload: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Marks an unclaimed person as ignored.

        Args:
            payload: Dictionary for the request body, typically including `personId`.

        Returns:
            A dictionary containing the API response or an error string.
        """
        return self._client._post("people/ignoreUnclaimed", json_data=payload)

    def add_tags(
        self,
        person_id: int,
        tags: List[str],
        *,
        merge: bool = True,
        case_sensitive: bool = True,
    ) -> Union[Dict[str, Any], str]:
        """
        Add or update tags on a person using the supported people update endpoint.

        This helper avoids unsupported endpoints like POST /people/{id}/tags which
        return 404 and instead performs a PUT to /people/{id} with the correct
        tags payload. When ``merge`` is True (default), existing tags are fetched,
        combined with the provided ones, and de-duplicated before updating. When
        ``merge`` is False, the provided ``tags`` replace any existing tags.

        Args:
            person_id: The ID of the person whose tags will be updated.
            tags: The list of tags to add (or set when ``merge`` is False).
            merge: If True, append to existing tags with de-duplication. If False,
                replace existing tags with the provided list. Defaults to True.
            case_sensitive: Controls de-duplication behavior. When True, 'Tag' and
                'tag' are treated as distinct. When False, comparisons are case-insensitive.
                Defaults to True.

        Returns:
            The updated person object on success, or an error string from the client.

        Raises:
            ValueError: If ``tags`` is empty.
        """
        if not tags:
            raise ValueError("'tags' must contain at least one tag")

        # Normalize provided tags: ensure all are strings and strip whitespace
        provided_tags: List[str] = [str(t).strip() for t in tags if str(t).strip()]
        if not provided_tags:
            raise ValueError("'tags' must contain at least one non-empty tag")

        updated_tags: List[str]

        if merge:
            # Fetch current tags from the person
            current_person = self.retrieve_person(person_id)
            existing_tags_raw = current_person.get("tags", [])
            existing_tags: List[str] = [
                str(t).strip() for t in existing_tags_raw if str(t).strip()
            ]

            if case_sensitive:
                # Preserve order: existing first, then new tags not already present
                seen = set(existing_tags)
                updated_tags = list(existing_tags)
                for t in provided_tags:
                    if t not in seen:
                        updated_tags.append(t)
                        seen.add(t)
            else:
                # Case-insensitive de-duplication while preserving original casing
                seen_lower = {t.lower(): t for t in existing_tags}
                # Add any new tags whose lowercase key isn't present
                for t in provided_tags:
                    key = t.lower()
                    if key not in seen_lower:
                        seen_lower[key] = t
                # Preserve original order preference: existing first, then new ones in input order
                existing_order = [seen_lower[t.lower()] for t in existing_tags]
                # Build remaining new tags in provided order
                new_order = []
                existing_keys = {t.lower() for t in existing_tags}
                for t in provided_tags:
                    if t.lower() not in existing_keys and t not in new_order:
                        new_order.append(t)
                updated_tags = existing_order + new_order
        else:
            # Replace mode: de-duplicate within provided tags based on case sensitivity
            if case_sensitive:
                seen_replace = set()
                updated_tags = []
                for t in provided_tags:
                    if t not in seen_replace:
                        updated_tags.append(t)
                        seen_replace.add(t)
            else:
                seen_lower_replace = set()
                updated_tags = []
                for t in provided_tags:
                    key = t.lower()
                    if key not in seen_lower_replace:
                        updated_tags.append(t)
                        seen_lower_replace.add(key)

        # Perform the update via the supported endpoint
        return self.update_person(person_id, {"tags": updated_tags})

    def list_people_by_list_id(
        self,
        list_id: int,
        *,
        limit: int = 100,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch a single page of people filtered by a Follow Up Boss Smart List ID.

        Args:
            list_id: Follow Up Boss List ID (must be a positive integer).
            limit: Page size for the request. Defaults to 100.
            next_token: Optional cursor token from a previous response's
                ``_metadata.next`` field to continue pagination.

        Returns:
            A dictionary response from the API that typically contains keys like
            ``"people"`` (a list of person dictionaries) and ``"_metadata"`` with
            pagination info such as ``"next"`` and ``"nextLink"``.

        Raises:
            ValueError: If ``list_id`` is not a positive integer.
            FollowUpBossApiException: If the API request fails.
        """
        if not isinstance(list_id, int) or list_id <= 0:
            raise ValueError("list_id must be a positive integer")

        params: Dict[str, Union[int, str]] = {"listId": list_id, "limit": limit}
        if next_token:
            params["next"] = next_token

        return self._client._get("people", params=params)

    def fetch_all_people_by_list_id(
        self,
        list_id: int,
        *,
        limit: int = 100,
        max_pages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all people for a given Smart List ID following cursor pagination.

        This helper repeatedly calls :py:meth:`list_people_by_list_id` and follows the
        ``_metadata.next`` token until there are no more pages or ``max_pages`` is
        reached.

        Args:
            list_id: Follow Up Boss List ID (must be a positive integer).
            limit: Page size per API request. Defaults to 100.
            max_pages: Optional safety cap for the maximum number of pages to fetch.
                When ``None`` (default), all pages are fetched until no ``next`` token
                is returned.

        Returns:
            A list of people dictionaries aggregated across all fetched pages.

        Raises:
            ValueError: If ``list_id`` is not a positive integer.
            FollowUpBossApiException: If any API call fails.
        """
        if not isinstance(list_id, int) or list_id <= 0:
            raise ValueError("list_id must be a positive integer")

        aggregated_people: List[Dict[str, Any]] = []
        next_token: Optional[str] = None
        pages_fetched: int = 0

        while True:
            page: Dict[str, Any] = self.list_people_by_list_id(
                list_id=list_id, limit=limit, next_token=next_token
            )
            people: List[Dict[str, Any]] = (
                page.get("people", []) if isinstance(page, dict) else []
            )
            aggregated_people.extend(people)

            meta: Dict[str, Any] = (
                page.get("_metadata", {}) if isinstance(page, dict) else {}
            )
            next_token = meta.get("next")
            pages_fetched += 1

            if not next_token:
                break
            if max_pages is not None and pages_fetched >= max_pages:
                break

        return aggregated_people

    def iter_people(
        self, params: Optional[ListPeopleParams] = None
    ) -> Iterator[Person]:
        """
        Iterate over people across all pages.

        Supports both offset-based and cursor-based pagination. When a response
        contains ``_metadata.next``, subsequent requests will include the
        corresponding ``next`` cursor token. Otherwise, the iterator falls back
        to offset-based pagination by incrementing the ``offset`` parameter.

        Args:
            params: Optional query parameters to filter and page results. Supports
                ``limit``, ``offset``, and optionally ``listId`` and ``next``.

        Yields:
            Person dictionaries one-by-one.
        """
        query: Dict[str, Any] = dict(params or {})
        limit: int = int(query.get("limit", 100) or 100)
        offset: int = int(query.get("offset", 0) or 0)
        next_token = cast(Optional[str], query.get("next"))

        while True:
            # Build params for this iteration
            page_params: Dict[str, Any] = dict(query)
            page_params["limit"] = limit
            if next_token:
                page_params.pop("offset", None)
                page_params["next"] = next_token
            else:
                page_params["offset"] = offset

            page = self.list_people(cast(ListPeopleParams, page_params))
            people: List[Person] = (
                page.get("people", []) if isinstance(page, dict) else []
            )
            for person in people:
                yield person

            # Determine next step
            meta: Dict[str, Any] = (
                page.get("_metadata", {}) if isinstance(page, dict) else {}
            )
            next_link: Optional[str] = meta.get("nextLink")
            if next_link:
                # Traverse absolute nextLink until exhausted
                while next_link:
                    page = cast(
                        PeopleListResponse, self._client.get_absolute(next_link)
                    )
                    people = page.get("people", []) if isinstance(page, dict) else []
                    for person in people:
                        yield person
                    meta = page.get("_metadata", {}) if isinstance(page, dict) else {}
                    next_link = meta.get("nextLink")
                break
            # Cursor token path (legacy)
            next_token = meta.get("next")
            if next_token:
                continue
            # Fallback to offset-based pagination
            if not people:
                break
            offset += len(people)
            if len(people) < limit:
                break

    def list_people_next(self, next_link: str) -> PeopleListResponse:
        """
        Fetch the next page using the API-provided absolute nextLink.

        Args:
            next_link: Absolute URL from ``_metadata['nextLink']``.

        Returns:
            Same response shape as :py:meth:`list_people`.
        """
        response = self._client.get_absolute(next_link)
        if isinstance(response, dict):
            response.setdefault("people", [])
            meta: Dict[str, Any] = cast(Dict[str, Any], response.get("_metadata", {}))
            response.setdefault("_metadata", meta)
        return cast(PeopleListResponse, response)
