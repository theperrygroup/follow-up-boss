"""
API bindings for Follow Up Boss Threaded Replies endpoints.
"""

from typing import Any, Dict

from .api_client import ApiClient, FollowUpBossApiException
import logging

logger = logging.getLogger(__name__)

class ThreadedReplies:
    """
    Provides access to the Threaded Replies endpoints of the Follow Up Boss API.
    Threaded replies are likely comments or replies to primary communication items like notes or emails.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the ThreadedReplies resource.

        Args:
            client: An instance of the ApiClient.
        """
        self.client = client

    def get_threaded_reply(self, reply_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific threaded reply by its ID.

        Args:
            reply_id: The ID of the threaded reply to retrieve.

        Returns:
            A dictionary containing the details of the threaded reply.
        """
        endpoint = f"/threadedReplies/{reply_id}"
        try:
            return self.client.get(endpoint)
        except FollowUpBossApiException as e:
            logger.error(f"API error retrieving threaded reply {reply_id}: {e}")
            raise 