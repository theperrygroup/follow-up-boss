"""
API bindings for Follow Up Boss Timeframes endpoint.
"""

from typing import Any, Dict, Optional

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class Timeframes:
    """
    Provides access to the Timeframes endpoint of the Follow Up Boss API.
    This endpoint likely lists predefined timeframes used in reporting or filtering.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the Timeframes resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_timeframes(self, **kwargs: Any) -> Dict[str, Any]: 
        """
        Retrieves a list of available timeframes.

        Args:
            **kwargs: Additional query parameters if any are supported.

        Returns:
            A dictionary containing the list of timeframes.
        """
        params: Dict[str, Any] = {}
        params.update(kwargs)
        
        return self._client.get("/timeframes", params=params) 