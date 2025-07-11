"""
API bindings for Follow Up Boss Action Plans endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class ActionPlans:
    """
    Provides access to the Action Plans endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the ActionPlans resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_action_plans(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters if specified by API docs (e.g., status, type)
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of Action Plans.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of Action Plans and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("actionPlans", params=params)

    def list_action_plan_assignments(
        self,
        action_plan_id: Optional[int] = None,
        person_id: Optional[int] = None,  # Filter by person
        status: Optional[str] = None,  # e.g., "Active", "Paused", "Finished"
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of people assigned to action plans (action plan assignments).

        Args:
            action_plan_id: Optional. Filter by a specific action plan ID.
            person_id: Optional. Filter assignments for a specific person.
            status: Optional. Filter by assignment status (e.g., "Active", "Paused").
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by.
            **kwargs: Additional query parameters.

        Returns:
            A dictionary containing the list of action plan assignments.
        """
        params: Dict[str, Any] = {}
        if action_plan_id is not None:
            params["actionPlanId"] = action_plan_id
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

        return self.client._get("actionPlansPeople", params=params)

    def assign_person_to_action_plan(
        self,
        person_id: int,
        action_plan_id: int,
        # Optional: start_date, status, etc., if supported by API for assignment
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Assigns a person to a specific action plan.

        Args:
            person_id: The ID of the person to assign.
            action_plan_id: The ID of the action plan to assign the person to.
            **kwargs: Additional parameters for the assignment (e.g., startDate).

        Returns:
            A dictionary containing the details of the action plan assignment or an error string.
        """
        payload = {"personId": person_id, "actionPlanId": action_plan_id}
        payload.update(kwargs)

        return self.client._post("actionPlansPeople", json_data=payload)

    def update_action_plan_assignment(
        self, assignment_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing action plan assignment for a person.
        This could be used to pause, resume, or finish an action plan for a person,
        or change its start date, depending on what the API supports.

        Args:
            assignment_id: The ID of the action plan assignment record to update.
                           (This is typically different from person_id or action_plan_id).
            update_data: A dictionary containing the fields to update
                         (e.g., {"status": "Paused"}).

        Returns:
            A dictionary containing the details of the updated action plan assignment or an error string.
        """
        return self.client._put(
            f"actionPlansPeople/{assignment_id}", json_data=update_data
        )

    # GET /actionPlansPeople (List people in action plans)
    # POST /actionPlansPeople (Add person to action plan)
    # PUT /actionPlansPeople/{id} (Update person in action plan)

    # ... rest of the file remains unchanged ...
