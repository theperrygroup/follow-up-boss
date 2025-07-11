"""
API bindings for Follow Up Boss Teams endpoints.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Teams:
    """
    Provides access to the Teams endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Teams resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_teams(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of teams in the account.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of teams and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self._client._get("teams", params=params)

    def create_team(
        self,
        name: str,
        user_ids: Optional[List[int]] = None,  # List of user IDs for team members
        leader_id: Optional[int] = None,  # User ID of the team leader
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new team.

        Args:
            name: The name of the team.
            user_ids: Optional. A list of user IDs to add as members to this team.
            leader_id: Optional. The User ID of the team leader.
            **kwargs: Additional fields for the team payload.

        Returns:
            A dictionary containing the details of the newly created team.
        """
        payload: Dict[str, Any] = {"name": name}
        if user_ids is not None:
            payload["userIds"] = user_ids  # Or 'users', 'members' - API specific
        if leader_id is not None:
            payload["leaderId"] = leader_id  # Or 'leader'

        payload.update(kwargs)

        return self._client._post("teams", json_data=payload)

    def retrieve_team(self, team_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific team by its ID.

        Args:
            team_id: The ID of the team to retrieve.

        Returns:
            A dictionary containing the details of the team.
        """
        return self._client._get(f"teams/{team_id}")

    def update_team(
        self, team_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing team.

        Args:
            team_id: The ID of the team to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Team Name"}).

        Returns:
            A dictionary containing the details of the updated team.
        """
        return self._client._put(f"teams/{team_id}", json_data=update_data)

    def delete_team(self, team_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific team by its ID.

        Args:
            team_id: The ID of the team to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client._delete(f"teams/{team_id}")

    # GET /teams/{id} (Retrieve team)
    # PUT /teams/{id} (Update team)
    # DELETE /teams/{id} (Delete team)
