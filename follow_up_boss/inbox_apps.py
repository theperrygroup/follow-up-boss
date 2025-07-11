"""
Handles the Inbox Apps endpoints for the Follow Up Boss API.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class InboxApps:
    """
    A class for interacting with the Inbox Apps endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the InboxApps resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def install_inbox_app(
        self, app_name: str, app_id: str, username: str, **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Installs an inbox app.

        Args:
            app_name: The name of the inbox app.
            app_id: The ID of the app.
            username: The username for the app.
            **kwargs: Additional fields for the install payload.

        Returns:
            A dictionary containing the installation details.
        """
        payload: Dict[str, Any] = {
            "appName": app_name,
            "appId": app_id,
            "username": username,
        }

        payload.update(kwargs)

        return self._client._post("inboxApps/install", json_data=payload)

    def add_message(
        self,
        conversation_id: str,
        body: str,
        sender: str,
        timestamp: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Adds a message to an inbox app conversation.

        Args:
            conversation_id: The ID of the conversation to add the message to.
            body: The message body.
            sender: The sender of the message.
            timestamp: Optional. The timestamp of the message (ISO 8601 format).
            **kwargs: Additional fields for the message payload.

        Returns:
            A dictionary containing the message details.
        """
        payload: Dict[str, Any] = {
            "conversationId": conversation_id,
            "body": body,
            "sender": sender,
        }

        if timestamp is not None:
            payload["timestamp"] = timestamp

        payload.update(kwargs)

        return self._client._post("inboxApps/addMessage", json_data=payload)

    def update_message(
        self, message_id: str, **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Updates a message in an inbox app conversation.

        Args:
            message_id: The ID of the message to update.
            **kwargs: Fields to update (e.g., body, status).

        Returns:
            A dictionary containing the updated message details.
        """
        payload: Dict[str, Any] = {"messageId": message_id}

        payload.update(kwargs)

        return self._client._put("inboxApps/updateMessage", json_data=payload)

    def add_note(
        self,
        conversation_id: str,
        body: str,
        created_by: str,
        timestamp: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Adds a note to an inbox app conversation.

        Args:
            conversation_id: The ID of the conversation to add the note to.
            body: The note body.
            created_by: The creator of the note.
            timestamp: Optional. The timestamp of the note (ISO 8601 format).
            **kwargs: Additional fields for the note payload.

        Returns:
            A dictionary containing the note details.
        """
        payload: Dict[str, Any] = {
            "conversationId": conversation_id,
            "body": body,
            "createdBy": created_by,
        }

        if timestamp is not None:
            payload["timestamp"] = timestamp

        payload.update(kwargs)

        return self._client._post("inboxApps/addNote", json_data=payload)

    def update_conversation(
        self, conversation_id: str, **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an inbox app conversation.

        Args:
            conversation_id: The ID of the conversation to update.
            **kwargs: Fields to update (e.g., title, status).

        Returns:
            A dictionary containing the updated conversation details.
        """
        payload: Dict[str, Any] = {"conversationId": conversation_id}

        payload.update(kwargs)

        return self._client._put("inboxApps/updateConversation", json_data=payload)

    def get_participants(self, conversation_id: str) -> Union[Dict[str, Any], str]:
        """
        Gets the participants of an inbox app conversation.

        Args:
            conversation_id: The ID of the conversation.

        Returns:
            A dictionary containing the participants.
        """
        params: Dict[str, Any] = {"conversationId": conversation_id}

        return self._client._get("inboxApps/getParticipants", params=params)

    def add_participant(
        self,
        conversation_id: str,
        participant_id: str,
        participant_type: str,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Adds a participant to an inbox app conversation.

        Args:
            conversation_id: The ID of the conversation.
            participant_id: The ID of the participant to add.
            participant_type: The type of participant (e.g., "user", "person").
            **kwargs: Additional fields for the participant payload.

        Returns:
            A dictionary containing the participant details.
        """
        payload: Dict[str, Any] = {
            "conversationId": conversation_id,
            "participantId": participant_id,
            "participantType": participant_type,
        }

        payload.update(kwargs)

        return self._client._post("inboxApps/addParticipant", json_data=payload)

    def remove_participant(
        self, conversation_id: str, participant_id: str, participant_type: str
    ) -> Union[Dict[str, Any], str]:
        """
        Removes a participant from an inbox app conversation.

        Args:
            conversation_id: The ID of the conversation.
            participant_id: The ID of the participant to remove.
            participant_type: The type of participant (e.g., "user", "person").

        Returns:
            A dictionary containing the result of the operation.
        """
        params: Dict[str, Any] = {
            "conversationId": conversation_id,
            "participantId": participant_id,
            "participantType": participant_type,
        }

        return self._client._delete("inboxApps/removeParticipant", data=params)

    def deactivate(self, app_id: str) -> Union[Dict[str, Any], str]:
        """
        Deactivates an inbox app.

        Args:
            app_id: The ID of the app to deactivate.

        Returns:
            A dictionary containing the result of the operation.
        """
        params: Dict[str, Any] = {"appId": app_id}

        return self._client._delete("inboxApps/deactivate", data=params)
