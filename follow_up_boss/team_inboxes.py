"""
API bindings for Follow Up Boss Team Inboxes endpoints.
"""

import logging
from typing import Any, Dict, Optional

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class TeamInboxes:
    """
    Provides access to the Team Inboxes endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the TeamInboxes resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_team_inboxes(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters if specified by API docs
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of team inboxes.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of team inboxes and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("teamInboxes", params=params)
