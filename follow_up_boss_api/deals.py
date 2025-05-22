"""
API bindings for Follow Up Boss Deals endpoints.
"""

from typing import Any, Dict, Optional, List

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class Deals:
    """
    Provides access to the Deals endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the Deals resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_deals(
        self,
        pipeline_id: Optional[int] = None,
        stage_id: Optional[int] = None,
        person_id: Optional[int] = None,
        status: Optional[str] = None, # e.g., "Open", "Won", "Lost"
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters like price, closeDateFrom, closeDateTo
        **kwargs: Any
    ) -> Dict[str, Any]: 
        """
        Retrieves a list of deals.

        Args:
            pipeline_id: Optional. Filter deals by a specific pipeline ID.
            stage_id: Optional. Filter deals by a specific stage ID.
            person_id: Optional. Filter deals associated with a specific person ID.
            status: Optional. Filter deals by status.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'closeDate', '-created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of deals and pagination information.
        """
        params: Dict[str, Any] = {}
        if pipeline_id is not None:
            params["pipelineId"] = pipeline_id
        if stage_id is not None:
            params["stageId"] = stage_id
        if person_id is not None:
            params["personId"] = person_id
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client.get("/deals", params=params)

    def create_deal(
        self,
        name: str,
        pipeline_id: int,
        stage_id: int,
        owner_id: int,
        person_id: Optional[int] = None, # This will be the ID of the primary contact
        price: Optional[float] = None,
        close_date: Optional[str] = None, # YYYY-MM-DD
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new deal.

        Args:
            name: The name of the deal.
            pipeline_id: The ID of the pipeline this deal belongs to.
            stage_id: The ID of the stage this deal is in.
            owner_id: The User ID of the owner of this deal.
            person_id: Optional. The ID of the primary Person associated with the deal.
            price: Optional. The value of the deal.
            close_date: Optional. The expected close date (YYYY-MM-DD).
            **kwargs: Additional fields for the deal payload.

        Returns:
            A dictionary containing the details of the newly created deal.
        """
        payload: Dict[str, Any] = {
            "name": name,
            "pipelineId": pipeline_id,
            "stageId": stage_id,
            "ownerId": owner_id
        }
        if person_id is not None:
            payload["contacts"] = [{"id": person_id}] # New way as per FUB docs for associating contacts
        if price is not None:
            payload["price"] = price
        if close_date is not None:
            payload["closeDate"] = close_date
        
        payload.update(kwargs)
        logger.debug(f"DEALS.CREATE_DEAL: Final payload before POST: {payload}")
        return self._client.post("/deals", json_data=payload)

    def retrieve_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific deal by its ID.

        Args:
            deal_id: The ID of the deal to retrieve.

        Returns:
            A dictionary containing the details of the deal.
        """
        return self._client.get(f"/deals/{deal_id}")

    def update_deal(self, deal_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing deal.

        Args:
            deal_id: The ID of the deal to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name", "price": 125000}).

        Returns:
            A dictionary containing the details of the updated deal.
        """
        return self._client.put(f"/deals/{deal_id}", json_data=update_data)

    def delete_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Deletes a specific deal by its ID.

        Args:
            deal_id: The ID of the deal to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/deals/{deal_id}")

    # GET /deals/{id} (Retrieve deal)
    # PUT /deals/{id} (Update deal)
    # DELETE /deals/{id} (Delete deal) 