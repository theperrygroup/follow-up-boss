"""
Handles the Ponds endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient


class Ponds:
    """
    A class for interacting with the Ponds endpoints of the Follow Up Boss API.

    Ponds are lead routing systems that distribute leads based on various criteria.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Ponds resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_ponds(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a list of ponds.

        Args:
            params: Optional. Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of ponds.
        """
        return self._client._get("ponds", params=params)

    def create_pond(
        self,
        name: str,
        user_ids: Optional[List[int]] = None,
        is_default: Optional[bool] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new pond.

        Args:
            name: The name of the pond.
            user_ids: Optional. List of user IDs (NOTE: API only accepts name field for creation).
            is_default: Optional. Whether this is the default pond (NOTE: Ignored by API).
            description: Optional. A description of the pond (NOTE: Ignored by API).
            **kwargs: Additional fields for the pond (NOTE: Most will be ignored by API).

        Returns:
            A dictionary containing the details of the newly created pond.

        Note:
            The Follow Up Boss Ponds API only accepts the "name" field for creation.
            All other fields are ignored. Use update_pond() to modify other properties after creation.
        """
        payload: Dict[str, Any] = {"name": name}

        return self._client._post("ponds", json_data=payload)

    def retrieve_pond(self, pond_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific pond by its ID.

        Args:
            pond_id: The ID of the pond to retrieve.

        Returns:
            A dictionary containing the pond details.
        """
        return self._client._get(f"ponds/{pond_id}")

    def update_pond(
        self,
        pond_id: int,
        name: Optional[str] = None,
        user_ids: Optional[List[int]] = None,
        is_default: Optional[bool] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing pond.

        Args:
            pond_id: The ID of the pond to update.
            name: Optional. The name of the pond.
            user_ids: Optional. List of user IDs that participate in this pond.
            is_default: Optional. Whether this is the default pond.
            description: Optional. A description of the pond.
            **kwargs: Additional fields to update.

        Returns:
            A dictionary containing the details of the updated pond.
        """
        payload: Dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if user_ids is not None:
            payload["users"] = user_ids
        if is_default is not None:
            payload["default"] = is_default
        if description is not None:
            payload["note"] = description

        payload.update(kwargs)

        return self._client._put(f"ponds/{pond_id}", json_data=payload)

    def delete_pond(
        self, pond_id: int, assign_to: Optional[int] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific pond by its ID.

        Args:
            pond_id: The ID of the pond to delete.
            assign_to: Optional. User ID to assign existing leads in this pond to.
                      If not provided, will try to use the current user.

        Returns:
            An empty dictionary if successful.

        Note:
            The Follow Up Boss API requires an "assignTo" parameter when deleting ponds
            to specify where to move any existing leads in the pond.
        """
        # API requires assignTo parameter for deletion
        if assign_to is None:
            # Try to get current user ID
            try:
                me = self._client._get("me")
                assign_to = me.get("id", 1)  # Default to 1 if can't get current user
            except:
                assign_to = 1  # Fallback default

        # Add assignTo as URL parameter
        url = f"ponds/{pond_id}?assignTo={assign_to}"
        return self._client._delete(url)
