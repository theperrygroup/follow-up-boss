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

    def pause_action_plan(
        self, assignment_id: int, reason: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Pause an action plan assignment for a person.

        This is a convenience method that wraps update_action_plan_assignment()
        with the appropriate status and reason fields.

        Args:
            assignment_id: The ID of the action plan assignment to pause.
            reason: Optional reason for pausing the action plan.

        Returns:
            A dictionary containing the updated action plan assignment or an error string.

        Example:
            >>> action_plans = ActionPlans(client)
            >>> result = action_plans.pause_action_plan(
            ...     assignment_id=12345,
            ...     reason="Communication detected"
            ... )
        """
        update_data = {"status": "paused"}
        if reason:
            update_data["pauseReason"] = reason

        return self.update_action_plan_assignment(assignment_id, update_data)

    def resume_action_plan(self, assignment_id: int) -> Union[Dict[str, Any], str]:
        """
        Resume a paused action plan assignment for a person.

        This is a convenience method that wraps update_action_plan_assignment()
        to set the status back to active.

        Args:
            assignment_id: The ID of the action plan assignment to resume.

        Returns:
            A dictionary containing the updated action plan assignment or an error string.

        Example:
            >>> action_plans = ActionPlans(client)
            >>> result = action_plans.resume_action_plan(assignment_id=12345)
        """
        update_data = {"status": "active"}
        return self.update_action_plan_assignment(assignment_id, update_data)

    def pause_all_for_person(
        self,
        person_id: int,
        reason: Optional[str] = None,
        only_active: bool = True,
    ) -> Dict[str, Any]:
        """
        Pause all action plan assignments for a specific person.

        This method fetches all action plan assignments for the person and
        pauses each one that matches the criteria.

        Args:
            person_id: The ID of the person whose action plans should be paused.
            reason: Optional reason for pausing the action plans.
            only_active: If True, only pause action plans with status="active".
                        If False, attempt to pause all action plans.

        Returns:
            A dictionary containing:
                - total_found: Total number of action plan assignments found
                - paused_count: Number of action plans successfully paused
                - failed_count: Number of action plans that failed to pause
                - errors: List of error messages for failed pauses

        Example:
            >>> action_plans = ActionPlans(client)
            >>> result = action_plans.pause_all_for_person(
            ...     person_id=67890,
            ...     reason="Communication detected"
            ... )
            >>> print(f"Paused {result['paused_count']} action plans")
        """
        # Fetch all action plan assignments for this person
        response = self.list_action_plan_assignments(person_id=person_id)

        # Handle different response formats
        assignments = response.get("actionPlansPeople", [])

        result: Dict[str, Any] = {
            "total_found": len(assignments),
            "paused_count": 0,
            "failed_count": 0,
            "errors": [],
        }

        for assignment in assignments:
            # Skip if only_active is True and this isn't active
            if only_active and assignment.get("status") != "active":
                continue

            assignment_id = assignment.get("id")
            if not assignment_id or not isinstance(assignment_id, (int, str)):
                result["failed_count"] += 1
                result["errors"].append("Assignment missing ID field")
                continue

            # Attempt to pause this assignment
            try:
                pause_result = self.pause_action_plan(assignment_id, reason)

                # Check if pause was successful
                if isinstance(pause_result, dict) and not pause_result.get("error"):
                    result["paused_count"] += 1
                else:
                    result["failed_count"] += 1
                    error_msg = f"Assignment {assignment_id}: {pause_result}"
                    result["errors"].append(error_msg)
            except Exception as e:
                result["failed_count"] += 1
                result["errors"].append(f"Assignment {assignment_id}: {str(e)}")

        return result

    # GET /actionPlansPeople (List people in action plans)
    # POST /actionPlansPeople (Add person to action plan)
    # PUT /actionPlansPeople/{id} (Update person in action plan)
