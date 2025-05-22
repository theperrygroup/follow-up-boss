"""
API bindings for Follow Up Boss Webhook Events endpoints.
"""

from typing import Any, Dict, Union

from .client import FollowUpBossApiClient
import logging

logger = logging.getLogger(__name__)

class WebhookEvents:
    """
    Provides access to the Webhook Events endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the WebhookEvents resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def retrieve_webhook_event(self, event_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves a specific webhook event by its ID.

        Args:
            event_id: The ID of the webhook event to retrieve.

        Returns:
            A dictionary containing the details of the webhook event.
        """
        return self.client._get(f"webhookEvents/{event_id}")
    
    # Alias for backward compatibility
    get_webhook_event = retrieve_webhook_event 