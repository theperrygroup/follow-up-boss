"""
API bindings for Follow Up Boss Webhook Events endpoints.
"""

from typing import Any, Dict

from .api_client import ApiClient, FollowUpBossApiException
import logging

logger = logging.getLogger(__name__)

class WebhookEvents: # Ensure class name is exactly WebhookEvents
    """
    Provides access to the Webhook Events endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the WebhookEvents resource.

        Args:
            client: An instance of the ApiClient.
        """
        self.client = client

    def get_webhook_event(self, event_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific webhook event by its ID.

        Args:
            event_id: The ID of the webhook event to retrieve.

        Returns:
            A dictionary containing the details of the webhook event.
        """
        endpoint = f"/webhookEvents/{event_id}"
        try:
            return self.client.get(endpoint)
        except FollowUpBossApiException as e:
            logger.error(f"API error retrieving webhook event {event_id}: {e}")
            raise 