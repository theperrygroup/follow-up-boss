"""
API bindings for Follow Up Boss Inbox Apps endpoints.
"""

from typing import Any, Dict, Optional, List

from .api_client import ApiClient, FollowUpBossApiException
import logging

logger = logging.getLogger(__name__)

class InboxApps:
    """
    Provides access to the Inbox Apps endpoints of the Follow Up Boss API.
    These endpoints are typically used for integrating third-party messaging services.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the InboxApps resource.

        Args:
            client: An instance of the ApiClient.
        """
        self.client = client

    def install_app(self, name: str, type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Installs a new inbox app.

        Args:
            name: The name of the app being installed.
            type: The type of the app (e.g., 'custom', 'sms', specific integration type).
            settings: A dictionary of settings required for the app configuration.
                      (e.g., {"apiKey": "some_key", "phoneNumber": "+15551234567"})

        Returns:
            A dictionary containing the details of the installed app, including its ID.
        """
        endpoint = "/inboxApps/install"
        payload = {
            "name": name,
            "type": type,
            "settings": settings
        }
        return self.client.post(endpoint, json_data=payload)

    def add_message(
        self, 
        app_id: int, 
        conversation_id: str, 
        contact_id: int, 
        body: str, 
        message_type: str = "received", # "sent" or "received"
        subject: Optional[str] = None,
        user_id: Optional[int] = None, # FUB User ID if sent by a user
        external_id: Optional[str] = None, # ID from the external messaging service
        timestamp: Optional[str] = None # ISO 8601 timestamp
    ) -> Dict[str, Any]:
        """
        Adds a message to an inbox app conversation.
        """
        endpoint = "/inboxApps/addMessage"
        payload: Dict[str, Any] = {
            "appId": app_id,
            "conversationId": conversation_id,
            "contactId": contact_id,
            "body": body,
            "type": message_type
        }
        if subject: payload["subject"] = subject
        if user_id: payload["userId"] = user_id
        if external_id: payload["externalId"] = external_id
        if timestamp: payload["timestamp"] = timestamp
        return self.client.post(endpoint, json_data=payload)

    def update_message(
        self, 
        message_id: str, # Usually the external_id of the message
        app_id: int,
        status: Optional[str] = None, # e.g., "delivered", "read", "failed"
        failure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates the status of a message in an inbox app.
        """
        endpoint = "/inboxApps/updateMessage"
        payload: Dict[str, Any] = {"messageId": message_id, "appId": app_id}
        if status: payload["status"] = status
        if failure_reason: payload["failureReason"] = failure_reason
        return self.client.put(endpoint, json_data=payload)

    # Other InboxApp methods as per endpoint_tasks.md would follow a similar pattern:
    # - add_note_to_conversation
    # - update_conversation
    # - get_participants
    # - add_participant
    # - remove_participant
    # - deactivate_app (likely DELETE /inboxApps/deactivate with appId in payload or path)

    # For brevity, only implementing install, add_message, and update_message for now.
    # The rest can be added following their specific payload requirements.

    def deactivate_app(self, app_id: int) -> Dict[str, Any]:
        """
        Deactivates (uninstalls) an inbox app.

        Args:
            app_id: The ID of the app to deactivate.

        Returns:
            An empty dictionary on success or API specific response.
        """
        endpoint = "/inboxApps/deactivate"
        # API might expect appId in payload or as part of URL. Assuming payload for now.
        payload = {"appId": app_id}
        return self.client.delete(endpoint, json_data=payload)

    # Placeholder for other methods from endpoint_tasks.md if needed later
    def add_note_to_conversation(self, conversation_id: str, contact_id: int, body: str, **kwargs) -> Dict[str, Any]:
        # Actual payload needs to be defined based on API docs
        payload = {"conversationId": conversation_id, "contactId": contact_id, "body": body, **kwargs}
        return self.client.post("/inboxApps/addNote", json_data=payload)

    def update_conversation(self, conversation_id: str, **kwargs) -> Dict[str, Any]:
        payload = {"conversationId": conversation_id, **kwargs}
        return self.client.put("/inboxApps/updateConversation", json_data=payload)

    def get_participants(self, conversation_id: str, **kwargs) -> Dict[str, Any]:
        params = {"conversationId": conversation_id, **kwargs}
        return self.client.get("/inboxApps/getParticipants", params=params)

    def add_participant(self, conversation_id: str, contact_id: Optional[int] = None, user_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        payload = {"conversationId": conversation_id, **kwargs}
        if contact_id: payload["contactId"] = contact_id
        if user_id: payload["userId"] = user_id
        return self.client.post("/inboxApps/addParticipant", json_data=payload)

    def remove_participant(self, conversation_id: str, contact_id: Optional[int] = None, user_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        # DELETE for this might expect IDs in query params or body.
        # Assuming body for now, similar to other app operations.
        payload = {"conversationId": conversation_id, **kwargs}
        if contact_id: payload["contactId"] = contact_id
        if user_id: payload["userId"] = user_id
        return self.client.delete("/inboxApps/removeParticipant", json_data=payload)
