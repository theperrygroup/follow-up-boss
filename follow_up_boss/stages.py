"""
API bindings for Follow Up Boss Stages endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Stages:
    """
    Provides access to the Stages endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Stages resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_stages(
        self,
        # Add relevant filters if specified by API docs (e.g., pipelineId, type)
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of stages defined in the account.

        Args:
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of stages.
            The FUB API often returns {"stages": [...]} or similar.
        """
        params: Dict[str, Any] = {}
        params.update(kwargs)

        return self._client._get("stages", params=params)

    def create_stage(
        self,
        name: str,
        pipeline_id: Optional[int] = None,
        # entity_type: Optional[str] = "Person",
        # order: Optional[int] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new stage.

        Args:
            name: The name of the stage.
            pipeline_id: Optional. The ID of the pipeline this stage belongs to.
            # entity_type: Optional. The type of entity this stage is for (e.g., "Person", "Deal").
            # order: Optional. The order of the stage in its pipeline.
            **kwargs: Additional fields for the stage payload.

        Returns:
            A dictionary containing the details of the newly created stage.
        """
        payload: Dict[str, Any] = {"name": name}
        if pipeline_id is not None:
            payload["pipelineId"] = pipeline_id

        # Remove these from kwargs if they were passed to avoid duplication or conflict if dev passed them via kwargs
        kwargs.pop("pipeline_id", None)
        kwargs.pop("pipelineId", None)

        payload.update(kwargs)

        return self._client._post("stages", json_data=payload)

    def retrieve_stage(self, stage_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific stage by its ID.

        Args:
            stage_id: The ID of the stage to retrieve.

        Returns:
            A dictionary containing the details of the stage.
        """
        return self._client._get(f"stages/{stage_id}")

    def update_stage(
        self, stage_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing stage.

        Args:
            stage_id: The ID of the stage to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name"}).

        Returns:
            A dictionary containing the details of the updated stage.
        """
        return self._client._put(f"stages/{stage_id}", json_data=update_data)

    def delete_stage(
        self, stage_id: int, assign_stage_id: Optional[int] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific stage by its ID.

        Args:
            stage_id: The ID of the stage to delete.
            assign_stage_id: Optional. The ID of the stage to which people in the deleted stage
                             should be reassigned. Required by the Follow Up Boss API.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.

        Raises:
            ValueError: If assign_stage_id is not provided, as it's required by the API.
        """
        if assign_stage_id is None:
            raise ValueError("assign_stage_id is required when deleting a stage.")

        payload = {"assignStageId": assign_stage_id}
        return self._client._delete(f"stages/{stage_id}", json_data=payload)

    # GET /stages/{id} (Retrieve stage)
    # PUT /stages/{id} (Update stage)
    # DELETE /stages/{id} (Delete stage)
