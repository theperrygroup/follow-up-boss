"""
Webhook utilities for Follow Up Boss API.

This module provides helper functions for parsing and processing webhook
payloads from Follow Up Boss, including extracting person IDs from various
payload formats and fetching related resources.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


def get_event_name(payload: Any) -> str:
    """
    Extract the event name from a Follow Up Boss webhook payload.

    Args:
        payload: The webhook payload dictionary.

    Returns:
        The event name (e.g., 'peopleUpdated', 'textMessagesCreated'),
        or empty string if not found.

    Example:
        >>> event = get_event_name(webhook_payload)
        >>> if event == "textMessagesCreated":
        ...     # Handle text message creation
    """
    # Handle invalid payload types
    if not isinstance(payload, dict):
        return ""

    # Follow Up Boss may use 'type' or 'event'
    event_value = payload.get("type") or payload.get("event")

    # Check nested data
    if not event_value and isinstance(payload.get("data"), dict):
        event_value = payload["data"].get("type")

    return str(event_value or "")


def extract_person_id_from_payload(
    payload: Dict[str, Any], client: Optional[FollowUpBossApiClient] = None
) -> Optional[int]:
    """
    Extract a Follow Up Boss person ID from a webhook payload.

    This function handles various webhook payload formats and attempts to
    extract the person ID using multiple strategies:

    1. Direct fields like 'personId' in payload or payload['data']
    2. For 'people*' events, uses 'resourceIds[0]' as personId
    3. For communication events (text/notes/calls/emails), fetches the
       resource and extracts its personId
    4. Fallback to URI query parameters

    Args:
        payload: The webhook payload dictionary.
        client: Optional FollowUpBossApiClient instance. Required for
                fetching resources in communication events.

    Returns:
        The person ID as an integer if found, None otherwise.

    Example:
        >>> from follow_up_boss import FollowUpBossApiClient
        >>> client = FollowUpBossApiClient(api_key="your_key")
        >>> person_id = extract_person_id_from_payload(webhook_payload, client)
        >>> if person_id:
        ...     print(f"Person ID: {person_id}")
    """
    # Strategy 1: Check common direct field paths
    person_id_paths = [
        "personId",
        "person.id",
        "data.personId",
        "data.person.id",
        "person_id",
        "data.person_id",
    ]

    for path in person_id_paths:
        person_id = _extract_from_path(payload, path)
        if person_id is not None:
            logger.debug(f"Found person_id via path '{path}': {person_id}")
            return person_id

    # Strategy 2: Check resourceIds for people* events
    event_name = get_event_name(payload)

    if not event_name or event_name.startswith("people"):
        person_id = _extract_from_resource_ids(payload)
        if person_id is not None:
            logger.debug(f"Found person_id via resourceIds: {person_id}")
            return person_id

    # Strategy 3: Fetch resource for communication events
    if client and event_name:
        person_id = _extract_from_resource_fetch(payload, event_name, client)
        if person_id is not None:
            logger.debug(f"Found person_id via resource fetch: {person_id}")
            return person_id

    # Strategy 4: Fallback to URI query parameters
    person_id = _extract_from_uri(payload)
    if person_id is not None:
        logger.debug(f"Found person_id via URI: {person_id}")
        return person_id

    logger.warning(
        "Could not extract person ID from webhook payload",
        extra={
            "payload_keys": list(payload.keys()) if isinstance(payload, dict) else None
        },
    )
    return None


def _extract_from_path(payload: Dict[str, Any], path: str) -> Optional[int]:
    """Extract value from nested dictionary path like 'data.person.id'."""
    curr: Any = payload
    for key in path.split("."):
        if isinstance(curr, dict):
            curr = curr.get(key)
        else:
            return None

        if curr is None:
            return None

    # Try to convert to int
    if isinstance(curr, int):
        return curr
    if isinstance(curr, str):
        try:
            return int(curr)
        except ValueError:
            return None

    return None


def _extract_from_resource_ids(payload: Dict[str, Any]) -> Optional[int]:
    """Extract person ID from resourceIds array."""

    resource_ids = payload.get("resourceIds")
    if not isinstance(resource_ids, list) or not resource_ids:
        return None

    first_id = resource_ids[0]

    if isinstance(first_id, int):
        return first_id
    if isinstance(first_id, str):
        try:
            return int(first_id)
        except ValueError:
            return None

    return None


def _extract_from_resource_fetch(
    payload: Dict[str, Any], event_name: str, client: FollowUpBossApiClient
) -> Optional[int]:
    """Fetch the resource and extract person ID from it."""
    # Import here to avoid circular imports
    from .calls import Calls
    from .events import Events
    from .notes import Notes
    from .text_messages import TextMessages

    # Map event names to resource classes
    resource_map = {
        "textMessagesCreated": ("textMessages", TextMessages),
        "notesCreated": ("notes", Notes),
        "callsCreated": ("calls", Calls),
        "emailsCreated": ("emails", Events),  # Emails might be under Events
    }

    if event_name not in resource_map:
        return None

    collection_name, resource_class = resource_map[event_name]

    # Get resource ID from payload
    resource_ids = payload.get("resourceIds")
    if not isinstance(resource_ids, list) or not resource_ids:
        return None

    resource_id = resource_ids[0]
    if isinstance(resource_id, str):
        try:
            resource_id = int(resource_id)
        except ValueError:
            return None

    if not isinstance(resource_id, int):
        return None

    # Fetch the resource
    try:
        resource_instance = resource_class(client)

        # Call the appropriate retrieve method
        if hasattr(resource_instance, "retrieve_text_message"):
            resource = resource_instance.retrieve_text_message(resource_id)
        elif hasattr(resource_instance, "retrieve_note"):
            resource = resource_instance.retrieve_note(resource_id)
        elif hasattr(resource_instance, "retrieve_call"):
            resource = resource_instance.retrieve_call(resource_id)
        elif hasattr(resource_instance, "retrieve_event"):
            resource = resource_instance.retrieve_event(resource_id)
        else:
            return None

        if isinstance(resource, dict):
            # Try to extract person ID from resource
            person_id = resource.get("personId") or resource.get("person_id")
            if isinstance(person_id, int):
                return person_id
            if isinstance(person_id, str):
                try:
                    return int(person_id)
                except ValueError:
                    return None

    except Exception as e:
        logger.warning(
            f"Failed to fetch resource for person ID extraction: {e}",
            extra={"event_name": event_name, "resource_id": resource_id},
        )

    return None


def _extract_from_uri(payload: Dict[str, Any]) -> Optional[int]:
    """Extract person ID from URI query parameter."""

    uri = payload.get("uri")
    if not isinstance(uri, str) or not uri:
        return None

    try:
        parsed = urlparse(uri)
        query_params = parse_qs(parsed.query)
        id_values = query_params.get("id", [])

        if isinstance(id_values, list) and id_values:
            try:
                return int(id_values[0])
            except ValueError:
                return None
    except Exception:
        pass

    return None


def get_resource_by_collection(
    client: FollowUpBossApiClient, collection: str, resource_id: int
) -> Optional[Dict[str, Any]]:
    """
    Fetch a resource by collection name and ID.

    This is a generic helper that routes to the appropriate resource class
    based on the collection name.

    Args:
        client: FollowUpBossApiClient instance.
        collection: Collection name (e.g., 'textMessages', 'notes', 'calls').
        resource_id: The resource ID to fetch.

    Returns:
        The resource dictionary if found, None otherwise.

    Example:
        >>> from follow_up_boss import FollowUpBossApiClient
        >>> client = FollowUpBossApiClient(api_key="your_key")
        >>> note = get_resource_by_collection(client, "notes", 12345)
    """
    # Import here to avoid circular imports
    from .calls import Calls
    from .events import Events
    from .notes import Notes
    from .text_messages import TextMessages

    if not collection or resource_id is None:
        return None

    try:
        if collection == "textMessages":
            text_messages = TextMessages(client)
            return text_messages.retrieve_text_message(resource_id)
        elif collection == "notes":
            notes = Notes(client)
            return notes.retrieve_note(resource_id)
        elif collection == "calls":
            calls = Calls(client)
            return calls.retrieve_call(resource_id)
        elif collection == "emails":
            events = Events(client)
            return events.retrieve_event(resource_id)
        else:
            logger.warning(f"Unknown collection: {collection}")
            return None

    except Exception as e:
        logger.error(
            f"Error fetching resource: {e}",
            extra={"collection": collection, "resource_id": resource_id},
        )
        return None
