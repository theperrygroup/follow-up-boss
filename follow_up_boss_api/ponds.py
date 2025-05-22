"""
API bindings for Follow Up Boss Ponds endpoints.
"""

from typing import Any, Dict, Optional, List

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class Ponds:
    """
    Provides access to the Ponds endpoints of the Follow Up Boss API.
    Ponds are used for managing leads that are not assigned to specific agents.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the Ponds resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_ponds(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters if specified by API docs (e.g., name)
        **kwargs: Any
    ) -> Dict[str, Any]: 
        """
        Retrieves a list of ponds in the account.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of ponds and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client.get("/ponds", params=params)

    def create_pond(
        self,
        name: str,
        user_ids: Optional[List[int]] = None, # List of user IDs for pond members
        # Add other relevant fields if specified by API (e.g., roundRobinEnabled)
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new pond.

        Args:
            name: The name of the pond.
            user_ids: Optional. A list of user IDs to add as members to this pond.
            **kwargs: Additional fields for the pond payload.

        Returns:
            A dictionary containing the details of the newly created pond.
        """
        payload: Dict[str, Any] = {"name": name}
        if user_ids is not None:
            payload["userIds"] = user_ids # Or 'users', 'members' - API specific
        
        payload.update(kwargs)
        
        return self._client.post("/ponds", json_data=payload)

    def retrieve_pond(self, pond_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific pond by its ID.

        Args:
            pond_id: The ID of the pond to retrieve.

        Returns:
            A dictionary containing the details of the pond.
        """
        return self._client.get(f"/ponds/{pond_id}")

    def update_pond(self, pond_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing pond.

        Args:
            pond_id: The ID of the pond to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Pond Name"}).

        Returns:
            A dictionary containing the details of the updated pond.
        """
        return self._client.put(f"/ponds/{pond_id}", json_data=update_data)

    def delete_pond(self, pond_id: int) -> Dict[str, Any]:
        """
        Deletes a specific pond by its ID.

        Args:
            pond_id: The ID of the pond to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/ponds/{pond_id}")

    # GET /ponds/{id} (Retrieve pond)
    # PUT /ponds/{id} (Update pond)
    # DELETE /ponds/{id} (Delete pond) 