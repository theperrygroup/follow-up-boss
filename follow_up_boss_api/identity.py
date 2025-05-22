"""
API bindings for Follow Up Boss Identity endpoint.
"""

from typing import Any, Dict

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class Identity:
    """
    Provides access to the Identity endpoint of the Follow Up Boss API.
    This typically returns information about the authenticated API key and account.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the Identity resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def get_identity(self) -> Dict[str, Any]: 
        """
        Retrieves identity information associated with the API key.

        Returns:
            A dictionary containing identity information.
        """
        return self._client.get("/identity") 