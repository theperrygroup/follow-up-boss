"""
API bindings for Follow Up Boss Webhooks endpoints.
"""

from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient
import logging

logger = logging.getLogger(__name__)

class Webhooks:
    """
    Provides access to the Webhooks endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Webhooks resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_webhooks(
        self,
        system: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs: Any
    ) -> Union[Dict[str, Any], str]: 
        """
        Retrieves a list of webhooks configured in the account.

        Args:
            system: The identifier for your system/integration.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'created', 'event').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of webhooks and pagination information.
        """
        params: Dict[str, Any] = {"system": system}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client._get("webhooks", params=params)

    def create_webhook(
        self,
        url: str,
        events: list[str], # List of event names to subscribe to
        system: str,
        # secret: Optional[str] = None, # Optional secret for verifying payload
        **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new webhook subscription.

        Args:
            url: The URL that Follow Up Boss will send POST requests to.
            events: A list of event names to subscribe to (e.g., ["person_created", "note_created"]).
            system: The identifier for your system/integration.
            # secret: Optional. A secret string for verifying incoming webhook payloads.
            **kwargs: Additional fields for the payload.

        Returns:
            A dictionary containing the details of the newly created webhook.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "events": events,
            "system": system
        }
        # if secret is not None:
        #     payload["secret"] = secret
        payload.update(kwargs)
        
        return self._client._post("webhooks", json_data=payload)

    def retrieve_webhook(self, webhook_id: int, system: str) -> Union[Dict[str, Any], str]:
        """
        Retrieves a specific webhook by its ID.

        Args:
            webhook_id: The ID of the webhook to retrieve.
            system: The identifier for your system/integration.

        Returns:
            A dictionary containing the details of the webhook.
        """
        return self._client.get(f"/webhooks/{webhook_id}", params={"system": system})

    def update_webhook(self, webhook_id: int, system: str, update_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Updates an existing webhook.

        Args:
            webhook_id: The ID of the webhook to update.
            system: The identifier for your system/integration.
            update_data: A dictionary containing the fields to update (e.g., {"url": "new_url", "events": ["new_event"]}).

        Returns:
            A dictionary containing the details of the updated webhook.
        """
        params = {"system": system}
        return self._client.put(f"/webhooks/{webhook_id}", json_data=update_data, params=params)

    def delete_webhook(self, webhook_id: int, system: str) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific webhook by its ID.

        Args:
            webhook_id: The ID of the webhook to delete.
            system: The identifier for your system/integration.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/webhooks/{webhook_id}", params={"system": system})

    def retrieve_webhook_event(self, event_id: Union[int, str], system: str) -> Union[Dict[str, Any], str]: # Event ID might be string
        """
        Retrieves details of a specific webhook event by its ID.

        Args:
            event_id: The ID of the webhook event to retrieve.
            system: The identifier for your system/integration.

        Returns:
            A dictionary containing the details of the webhook event.
        """
        return self._client.get(f"/webhookEvents/{event_id}", params={"system": system})

    # GET /webhooks/{id} (Retrieve webhook)
    # PUT /webhooks/{id} (Update webhook)
    # DELETE /webhooks/{id} (Delete webhook) 