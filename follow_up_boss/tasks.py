"""
API bindings for Follow Up Boss Tasks endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Tasks:
    """
    Provides access to the Tasks endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Tasks resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_tasks(
        self,
        person_id: Optional[int] = None,
        assigned_to: Optional[int] = None,  # User ID
        status: Optional[str] = None,  # e.g., "incomplete", "complete"
        due_date_from: Optional[str] = None,  # ISO 8601 YYYY-MM-DD
        due_date_to: Optional[str] = None,  # ISO 8601 YYYY-MM-DD
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Retrieves a list of tasks.

        Args:
            person_id: Optional. Filter tasks for a specific person ID.
            assigned_to: Optional. Filter tasks assigned to a specific user ID.
            status: Optional. Filter tasks by status (e.g., "incomplete", "complete").
            due_date_from: Optional. Filter tasks due on or after this date.
            due_date_to: Optional. Filter tasks due on or before this date.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'dueDate', '-created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of tasks and pagination information.
        """
        params: Dict[str, Any] = {}
        if person_id is not None:
            params["personId"] = person_id
        if assigned_to is not None:
            params["assignedTo"] = assigned_to
        if status is not None:
            params["status"] = status
        if due_date_from is not None:
            params["dueDateFrom"] = due_date_from
        if due_date_to is not None:
            params["dueDateTo"] = due_date_to
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("tasks", params=params)

    def create_task(
        self,
        name: str,
        person_id: Optional[int] = None,
        assigned_to: Optional[int] = None,  # This will be mapped to assigneeId
        due_date: Optional[str] = None,
        details: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new task.

        Args:
            name: The name/title of the task.
            person_id: Optional. The ID of the person associated with this task.
            assigned_to: Optional. User ID the task is assigned to.
            due_date: Optional. The due date for the task in ISO 8601 format (YYYY-MM-DD).
            details: Optional. Additional details or description for the task.
            **kwargs: Additional fields for the task payload.

        Returns:
            A dictionary containing the details of the newly created task.
        """
        payload: Dict[str, Any] = {"name": name}
        if person_id is not None:
            payload["personId"] = person_id
        if assigned_to is not None:
            payload["assigneeId"] = assigned_to
        if due_date is not None:
            payload["dueDate"] = due_date
        if details is not None:
            payload[
                "notes"
            ] = details  # Changed from description to notes based on API error

        # Remove any unexpected fields that might cause issues
        if "description" in kwargs:
            kwargs.pop("description")

        payload.update(kwargs)
        logger.debug(f"TASKS.CREATE_TASK: Final payload for POST /tasks: {payload}")
        return self.client._post("tasks", json_data=payload)

    def retrieve_task(self, task_id: int) -> Union[Dict[str, Any], str]:
        """
        Retrieves a specific task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            A dictionary containing the details of the task.
        """
        return self.client._get(f"tasks/{task_id}")

    def update_task(
        self, task_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing task.

        Args:
            task_id: The ID of the task to update.
            update_data: A dictionary containing the fields to update
                         (e.g., {"name": "New Task Name", "status": "complete", "dueDate": "YYYY-MM-DD"}).

        Returns:
            A dictionary containing the details of the updated task.
        """
        return self.client._put(f"tasks/{task_id}", json_data=update_data)

    def delete_task(self, task_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self.client._delete(f"tasks/{task_id}")

    # DELETE /tasks/{id} (Delete task)
