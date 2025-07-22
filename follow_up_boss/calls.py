"""
API bindings for Follow Up Boss Calls endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Calls:
    """
    Provides access to the Calls endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Calls resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_calls(
        self,
        person_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., outcome, duration, date ranges)
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of calls.

        Args:
            person_id: Optional. Filter calls for a specific person ID.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'created', '-created', 'duration').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of calls and pagination information.
        """
        params: Dict[str, Any] = {}
        if person_id is not None:
            params["personId"] = person_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("calls", params=params)

    def create_call(
        self,
        person_id: int,
        phone: str,  # Added: The phone number called or associated with the call
        duration: int,  # in seconds
        outcome: str,
        is_incoming: bool,  # Added: True if incoming call, False if outgoing
        note: Optional[str] = None,
        recording_url: Optional[str] = None,
        called_at: Optional[str] = None,  # ISO 8601 format e.g. "2023-01-15T14:30:00Z"
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new call log entry for a specific person.

        Args:
            person_id: The ID of the person associated with the call.
            phone: The phone number involved in the call.
            duration: Duration of the call in seconds.
            outcome: The outcome of the call (e.g., "Answered", "Left Voicemail").
                     Check FUB for a list of valid outcomes.
            is_incoming: Boolean indicating if the call was incoming or outgoing.
            note: Optional. A note or summary about the call.
            recording_url: Optional. URL to the call recording.
            called_at: Optional. The time the call occurred (ISO 8601). Defaults to now by API if not set.
            **kwargs: Additional fields for the call payload.

        Returns:
            A dictionary containing the details of the newly created call log or an error string.
        """
        payload: Dict[str, Any] = {
            "personId": person_id,
            "phone": phone,
            "duration": duration,
            "outcome": outcome,
            "isIncoming": is_incoming,
        }
        if note is not None:
            payload[
                "note"
            ] = note  # FUB docs refer to this as 'body' for some note-like objects
            # but 'note' is common for call logs directly.
        if recording_url is not None:
            payload["recordingUrl"] = recording_url
        if called_at is not None:
            payload["calledAt"] = called_at

        payload.update(kwargs)

        return self.client._post("calls", json_data=payload)

    def retrieve_call(self, call_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific call log by its ID.

        Args:
            call_id: The ID of the call log to retrieve.

        Returns:
            A dictionary containing the details of the call log.
        """
        return self.client._get(f"calls/{call_id}")

    def update_call(
        self, call_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing call log.

        Args:
            call_id: The ID of the call log to update.
            update_data: A dictionary containing the fields to update.
                         Common updatable fields might include 'outcome', 'note',
                         or 'duration'. personId is generally not updatable.

        Returns:
            A dictionary containing the details of the updated call log or an error string.
        """
        return self.client._put(f"calls/{call_id}", json_data=update_data)

    # GET /calls/{id} (Retrieve call)
    # PUT /calls/{id} (Update call)
