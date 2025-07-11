"""
Handles the Webhook Events endpoints for the Follow Up Boss API.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class WebhookEvents:
    """
    A class for interacting with the Webhook Events endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the WebhookEvents resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def retrieve_webhook_event(self, event_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves details of a specific webhook event by its ID.

        Args:
            event_id: The ID of the webhook event to retrieve.

        Returns:
            A dictionary containing the details of the webhook event.
        """
        return self._client._get(f"webhookEvents/{event_id}")

    # Alias for backward compatibility
    get_webhook_event = retrieve_webhook_event
