"""
API bindings for Follow Up Boss Groups endpoints.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Groups:
    """
    Provides access to the Groups endpoints of the Follow Up Boss API.
    These are typically user groups for lead distribution, permissions, etc.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Groups resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_groups(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., name, type)
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Retrieves a list of groups.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of groups and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self._client._get("groups", params=params)

    def get_group_round_robin_status(self, group_id: int) -> Union[Dict[str, Any], str]:
        """
        Retrieves the round robin status for a specific group.

        Args:
            group_id: The ID of the group.

        Returns:
            A dictionary containing the round robin status details.
        """
        # The endpoint structure might be /groups/{group_id}/roundRobin or /groups/roundRobin?groupId={group_id}
        # Based on the task list "GET /groups/roundRobin", it seems it might be a general endpoint
        # that perhaps takes groupId as a parameter, or it applies to the authenticated user's context implicitly.
        # For a specific group, /groups/{group_id}/roundRobin is more RESTful.
        # Let's assume it implies action on a specific group, thus needing group_id in path.
        # If it's a general status, the method signature and endpoint call would differ.
        # Given the task list formatting, it is ambiguous. Will assume /groups/{id}/roundRobin for now.
        # If error, will try /groups/roundRobin with groupId as param.

        # Correction based on common API patterns for sub-resources/actions:
        # /v1/groups/{id}/roundRobin is a more standard pattern for an action on a specific group.
        # The task list says GET /v1/groups/roundRobin -> this typically would not take an ID in path.
        # It might be that it gets round robin for *all* groups or for user context.
        # However, the test test_get_group_round_robin_status passes group_id, implying it IS per group.
        # Let's assume the path is /groups/{group_id}/roundRobin for now.
        # If error, will try /groups/roundRobin with groupId as param.
        return self._client._get(f"groups/{group_id}/roundRobin")

    def create_group(
        self,
        name: str,
        user_ids: Optional[
            List[int]
        ] = None,  # List of user IDs to be members of the group
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new group.

        Args:
            name: The name of the group.
            user_ids: Optional. A list of user IDs to add as members to this group.
            **kwargs: Additional fields for the group payload (e.g., settings for round robin).

        Returns:
            A dictionary containing the details of the newly created group.
        """
        payload: Dict[str, Any] = {"name": name}
        if user_ids is not None:
            payload["users"] = user_ids  # Try "users" instead of "userIds"

        payload.update(kwargs)

        return self._client._post("groups", json_data=payload)

    def retrieve_group(self, group_id: int) -> Union[Dict[str, Any], str]:
        """
        Retrieves a specific group by its ID.

        Args:
            group_id: The ID of the group to retrieve.

        Returns:
            A dictionary containing the details of the group.
        """
        return self._client._get(f"groups/{group_id}")

    def update_group(
        self, group_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing group.

        Args:
            group_id: The ID of the group to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Group Name"}).

        Returns:
            A dictionary containing the details of the updated group.
        """
        return self._client._put(f"groups/{group_id}", json_data=update_data)

    def delete_group(self, group_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific group by its ID.

        Args:
            group_id: The ID of the group to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client._delete(f"groups/{group_id}")

    # GET /groups/roundRobin (Get group round robin status)
    # POST /groups (Create group)
    # GET /groups/{id} (Retrieve group)
    # PUT /groups/{id} (Update group)
    # DELETE /groups/{id} (Delete group)
