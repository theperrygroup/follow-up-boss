"""
API bindings for Follow Up Boss Tasks endpoints.
"""

from typing import Any, Dict, Optional

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class Tasks:
    """
    Provides access to the Tasks endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the Tasks resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_tasks(
        self,
        person_id: Optional[int] = None,
        assigned_to: Optional[int] = None, # User ID
        status: Optional[str] = None, # e.g., "incomplete", "complete"
        due_date_from: Optional[str] = None, # ISO 8601 YYYY-MM-DD
        due_date_to: Optional[str] = None,   # ISO 8601 YYYY-MM-DD
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: 
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
        
        return self._client.get("/tasks", params=params)

    def create_task(
        self,
        name: str, 
        person_id: Optional[int] = None,
        assigned_to: Optional[int] = None, # This will be mapped to assigneeId
        due_date: Optional[str] = None, 
        details: Optional[str] = None, # This will be mapped to description
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new task.
        """
        payload: Dict[str, Any] = {"name": name}
        if person_id is not None: 
            payload["personId"] = person_id
        if assigned_to is not None: 
            payload["assigneeId"] = assigned_to # Try assigneeId
        if due_date is not None: 
            payload["dueDate"] = due_date
        if details is not None: 
            payload["description"] = details # Try description
        
        payload.update(kwargs)
        logger.debug(f"TASKS.CREATE_TASK: Final payload for POST /tasks: {payload}")
        return self._client.post("/tasks", json_data=payload)

    def retrieve_task(self, task_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            A dictionary containing the details of the task.
        """
        return self._client.get(f"/tasks/{task_id}")

    def update_task(self, task_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing task.

        Args:
            task_id: The ID of the task to update.
            update_data: A dictionary containing the fields to update 
                         (e.g., {"name": "New Task Name", "status": "complete", "dueDate": "YYYY-MM-DD"}).

        Returns:
            A dictionary containing the details of the updated task.
        """
        return self._client.put(f"/tasks/{task_id}", json_data=update_data)

    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Deletes a specific task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/tasks/{task_id}")

    # DELETE /tasks/{id} (Delete task) 