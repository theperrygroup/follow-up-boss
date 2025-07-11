"""
API bindings for Follow Up Boss Smart Lists endpoints.
"""

import logging
from typing import Any, Dict, Optional

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class SmartLists:
    """
    Provides access to the Smart Lists endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the SmartLists resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_smart_lists(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters if specified by API docs
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of Smart Lists.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of Smart Lists and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("smartLists", params=params)

    def retrieve_smart_list(self, smart_list_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific Smart List by its ID.

        Args:
            smart_list_id: The ID of the Smart List to retrieve.

        Returns:
            A dictionary containing the details of the Smart List.
        """
        return self.client._get(f"smartLists/{smart_list_id}")

    # GET /smartLists/{id} (Retrieve Smart List)
