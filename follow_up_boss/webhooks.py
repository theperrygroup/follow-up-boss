"""
Handles the Webhooks endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient


class Webhooks:
    """
    A class for interacting with the Webhooks endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Webhooks resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_webhooks(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a list of webhooks.

        Args:
            params: Optional. Additional parameters to filter the results.

        Returns:
            A dictionary containing the list of webhooks.
        """
        return self._client._get("webhooks", params=params)

    def create_webhook(
        self,
        url: str,
        event_types: List[str],
        name: Optional[str] = None,
        secret: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new webhook.

        Args:
            url: The URL that will receive webhook events.
            event_types: List of event types to subscribe to.
            name: Optional. A name for the webhook.
            secret: Optional. A secret token to validate webhooks.

        Returns:
            A dictionary containing the created webhook details.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "event": (
                event_types[0] if event_types else "peopleCreated"
            ),  # Use valid event: peopleCreated, peopleUpdated, etc.
        }

        if secret:
            payload["secret"] = secret

        return self._client._post("webhooks", json_data=payload)

    def retrieve_webhook(self, webhook_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific webhook by its ID.

        Args:
            webhook_id: The ID of the webhook to retrieve.

        Returns:
            A dictionary containing the webhook details.
        """
        return self._client._get(f"webhooks/{webhook_id}")

    def update_webhook(
        self,
        webhook_id: int,
        url: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        name: Optional[str] = None,
        secret: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing webhook.

        Args:
            webhook_id: The ID of the webhook to update.
            url: Optional. The URL that will receive webhook events.
            event_types: Optional. List of event types to subscribe to.
            name: Optional. A name for the webhook.
            secret: Optional. A secret token to validate webhooks.
            active: Optional. Whether the webhook is active.

        Returns:
            A dictionary containing the updated webhook details.
        """
        payload: Dict[str, Any] = {}

        if url is not None:
            payload["url"] = url
        if event_types is not None:
            payload["eventTypes"] = event_types
        if name is not None:
            payload["name"] = name
        if secret is not None:
            payload["secret"] = secret
        if active is not None:
            payload["active"] = active

        return self._client._put(f"webhooks/{webhook_id}", json_data=payload)

    def delete_webhook(self, webhook_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific webhook by its ID.

        Args:
            webhook_id: The ID of the webhook to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content).
        """
        return self._client._delete(f"webhooks/{webhook_id}")

    # GET /webhooks/{id} (Retrieve webhook)
    # PUT /webhooks/{id} (Update webhook)
    # DELETE /webhooks/{id} (Delete webhook)
