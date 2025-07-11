"""
API bindings for Follow Up Boss Pipelines endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Pipelines:
    """
    Provides access to the Pipelines endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Pipelines resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_pipelines(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., entityType like 'Deal')
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of pipelines.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of pipelines and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("pipelines", params=params)

    def create_pipeline(
        self,
        name: str,
        # entity_type: Optional[str] = "Deal", # Pipelines are often for Deals
        # stages: Optional[list[Dict[str, Any]]] = None, # Optional: define stages during pipeline creation
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new pipeline.

        Args:
            name: The name of the pipeline.
            # entity_type: Optional. The type of entity this pipeline is for (e.g., "Deal").
            # stages: Optional. A list of stage definitions to create within this pipeline.
            #         Each stage dict might contain {"name": "Stage Name", "order": 1, ...}
            **kwargs: Additional fields for the pipeline payload.

        Returns:
            A dictionary containing the details of the newly created pipeline or an error string.
        """
        payload: Dict[str, Any] = {"name": name}
        # if entity_type is not None:
        #     payload["entityType"] = entity_type
        # if stages is not None:
        #     payload["stages"] = stages # API structure for this needs verification

        payload.update(kwargs)

        return self.client._post("pipelines", json_data=payload)

    def retrieve_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific pipeline by its ID.

        Args:
            pipeline_id: The ID of the pipeline to retrieve.

        Returns:
            A dictionary containing the details of the pipeline.
        """
        return self.client._get(f"pipelines/{pipeline_id}")

    def update_pipeline(
        self, pipeline_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing pipeline.

        Args:
            pipeline_id: The ID of the pipeline to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name"}).

        Returns:
            A dictionary containing the details of the updated pipeline or an error string.
        """
        return self.client._put(f"pipelines/{pipeline_id}", json_data=update_data)

    def delete_pipeline(self, pipeline_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific pipeline by its ID.

        Args:
            pipeline_id: The ID of the pipeline to delete.

        Returns:
            An empty dictionary or string if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self.client._delete(f"pipelines/{pipeline_id}")

    # GET /pipelines/{id} (Retrieve pipeline)
    # PUT /pipelines/{id} (Update pipeline)
    # DELETE /pipelines/{id} (Delete pipeline)
