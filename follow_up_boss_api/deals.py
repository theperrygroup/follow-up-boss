"""
Handles the Deals endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, Optional, List, Union

from .client import FollowUpBossApiClient
import logging

logger = logging.getLogger(__name__)

class Deals:
    """
    A class for interacting with the Deals endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Deals resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
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
            params["pipeline_id"] = pipeline_id
        if stage_id is not None:
            params["stage_id"] = stage_id
        if person_id is not None:
            params["person_id"] = person_id
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client._get("deals", params=params)

    def create_deal(
        self,
        name: str,
        stage_id: int,
        pipeline_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        person_id: Optional[int] = None,
        price: Optional[float] = None,
        close_date: Optional[str] = None, # YYYY-MM-DD
        description: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new deal.

        Args:
            name: The name of the deal.
            stage_id: The ID of the stage this deal is in - REQUIRED by the API.
            pipeline_id: Optional. The ID of the pipeline this deal belongs to.
            owner_id: Optional. The User ID of the owner of this deal.
            person_id: Optional. The ID of the primary Person associated with the deal.
            price: Optional. The value of the deal.
            close_date: Optional. The expected close date (YYYY-MM-DD).
            description: Optional. A description of the deal.
            status: Optional. The status of the deal (e.g., "Active").
            **kwargs: Additional fields for the deal payload.

        Returns:
            A dictionary containing the details of the newly created deal.
        """
        # The API expects camelCase names with "stageId" being the only required field
        payload: Dict[str, Any] = {
            "name": name,
            "stageId": stage_id
        }
        
        # Add optional fields - note that the API rejects snake_case
        if pipeline_id is not None:
            payload["pipelineId"] = pipeline_id
        if owner_id is not None:
            payload["userId"] = owner_id  # API seems to expect userId not ownerId
        # if person_id is not None:
        #     payload["personId"] = person_id  # API rejects both contactId and personId
        if price is not None:
            payload["price"] = price
        if close_date is not None:
            payload["projectedCloseDate"] = close_date
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        logger.debug(f"DEALS.CREATE_DEAL: Final payload before POST: {payload}")
        return self._client._post("deals", json_data=payload)

    def retrieve_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific deal by its ID.

        Args:
            deal_id: The ID of the deal to retrieve.

        Returns:
            A dictionary containing the details of the deal.
        """
        return self._client._get(f"deals/{deal_id}")

    def update_deal(self, deal_id: int, update_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Updates an existing deal.

        Args:
            deal_id: The ID of the deal to update.
            update_data: A dictionary containing the fields to update.
                         Use camelCase for field names (e.g., {"name": "New Name", "price": 125000, "stageId": 25}).

        Returns:
            A dictionary containing the details of the updated deal.
        """
        return self._client._put(f"deals/{deal_id}", json_data=update_data)

    def delete_deal(self, deal_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific deal by its ID.

        Args:
            deal_id: The ID of the deal to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client._delete(f"deals/{deal_id}")

    # GET /deals/{id} (Retrieve deal)
    # PUT /deals/{id} (Update deal)
    # DELETE /deals/{id} (Delete deal) 