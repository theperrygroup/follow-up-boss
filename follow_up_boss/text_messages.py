"""
API bindings for Follow Up Boss Text Messages endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class TextMessages:
    """
    Provides access to the TextMessages endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the TextMessages resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_text_messages(
        self,
        person_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., direction, status, date ranges)
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of text messages.

        Args:
            person_id: Filter text messages for a specific person ID.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'created', '-created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of text messages and pagination information.
        """
        params: Dict[str, Any] = {}
        params["personId"] = person_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("textMessages", params=params)

    def create_text_message(
        self,
        person_id: int,
        message: str,
        to_number: str,  # Added: Phone number the message is sent to
        # FUB User ID or FUB Number ID from which the message is sent or to which it is received
        from_number: Optional[str] = None,  # Added: Number message is sent from
        contact_id: Optional[Union[int, str]] = None,
        is_incoming: Optional[bool] = False,
        # status: Optional[str] = None, # e.g., "Sent", "Delivered", "Failed"
        # sent_at: Optional[str] = None, # ISO 8601, defaults to now if not set
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Creates a new text message log.
        Note: This logs a text message, it may not actually send one depending on FUB capabilities.

        Args:
            person_id: The ID of the person associated with the text message.
            message: The content of the text message.
            to_number: The phone number the message is sent to.
            from_number: Optional. The phone number the message is sent from.
            contact_id: Optional. The ID of the FUB user or FUB phone number associated with sending/receiving.
                        This might be called `userId` or `fubNumberId` by the API.
            is_incoming: Boolean indicating if message is incoming (True) or outgoing (False).
                        Defaults to False (outgoing).
            **kwargs: Additional fields for the text message payload.

        Returns:
            A dictionary containing the details of the newly created text message log.
        """
        payload: Dict[str, Any] = {
            "personId": person_id,
            "message": message,
            "isIncoming": is_incoming,
            "toNumber": to_number,
        }
        if from_number is not None:
            payload["fromNumber"] = from_number
        if contact_id is not None:
            # The actual field name might be specific, e.g., "userId", "fubContactId"
            payload["contactId"] = contact_id

        payload.update(kwargs)

        return self.client._post("textMessages", json_data=payload)

    def retrieve_text_message(self, text_message_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific text message log by its ID.

        Args:
            text_message_id: The ID of the text message log to retrieve.

        Returns:
            A dictionary containing the details of the text message log.
        """
        return self.client._get(f"textMessages/{text_message_id}")

    # GET /textMessages/{id} (Retrieve text message)
