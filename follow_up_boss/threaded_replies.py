"""
API bindings for Follow Up Boss Threaded Replies endpoints.
"""

import logging
from typing import Any, Dict, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class ThreadedReplies:
    """
    Provides access to the Threaded Replies endpoints of the Follow Up Boss API.
    Threaded replies are likely comments or replies to primary communication items like notes or emails.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the ThreadedReplies resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def retrieve_threaded_reply(self, reply_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves a specific threaded reply by its ID.

        Args:
            reply_id: The ID of the threaded reply to retrieve.

        Returns:
            A dictionary containing the details of the threaded reply.
        """
        return self.client._get(f"threadedReplies/{reply_id}")

    # Alias for backward compatibility
    get_threaded_reply = retrieve_threaded_reply
