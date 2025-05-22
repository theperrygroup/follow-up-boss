"""
Test the Tasks API.
"""

import pytest
import uuid
from datetime import datetime, timedelta
import os
import requests
from follow_up_boss_api.client import FollowUpBossApiException
import json
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.tasks import Tasks


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )


@pytest.fixture
def tasks_api(client):
    """Create a Tasks API instance for testing."""
    return Tasks(client)


@pytest.fixture
def test_task_data():
    """Create test data for a task."""
    unique_suffix = uuid.uuid4().hex[:8]
    
    # Start with just a name - minimum required field
    return {
        "name": f"Test Task {unique_suffix}"
    }


def test_list_tasks(tasks_api):
    """Test listing tasks."""
    try:
        response = tasks_api.list_tasks(limit=10)
        
        # Debug output
        print("\n\nList Tasks Response:")
        print(json.dumps(response, indent=2))
        
        # Basic assertions
        assert isinstance(response, dict)
        assert "_metadata" in response
        
        # Check if the response has the expected structure
        metadata = response["_metadata"]
        assert "collection" in metadata
        assert metadata["collection"] == "tasks" or "task" in metadata["collection"].lower()
        
        # There should be a tasks array, though it might be empty
        collection_name = metadata["collection"]
        if collection_name in response:
            assert isinstance(response[collection_name], list)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            pytest.skip("API key doesn't have permission to list tasks")
        raise


def create_test_task(tasks_api, task_data):
    """
    Helper function to create a test task.
    
    Args:
        tasks_api: The Tasks API instance.
        task_data: Dictionary with task data.
        
    Returns:
        The ID of the created task and the response data.
    """
    try:
        response = tasks_api.create_task(**task_data)
        
        # Debug output
        print("\n\nCreate Task Response:")
        print(json.dumps(response, indent=2))
        
        if isinstance(response, dict) and "id" in response:
            return response["id"], response
        else:
            pytest.skip(f"Could not create test task, unexpected response: {response}")
            return None, None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error creating task: {e}")
        print(f"Response content: {e.response.content if hasattr(e, 'response') else ''}")
        
        if e.response.status_code == 403:
            pytest.skip("API key doesn't have permission to create tasks")
        raise


def test_create_and_retrieve_task(tasks_api, test_task_data):
    """Test creating and then retrieving a task."""
    try:
        # Create a task
        task_id, create_response = create_test_task(tasks_api, test_task_data)
        
        if not task_id:
            pytest.skip("Could not create test task")
        
        # Retrieve the task
        retrieve_response = tasks_api.retrieve_task(task_id)
        
        # Debug output
        print("\n\nRetrieve Task Response:")
        print(json.dumps(retrieve_response, indent=2))
        
        # Verify task details
        assert isinstance(retrieve_response, dict)
        assert "id" in retrieve_response
        assert retrieve_response["id"] == task_id
        assert "name" in retrieve_response
        assert retrieve_response["name"] == test_task_data["name"]
        
        # Clean up - delete the task
        try:
            tasks_api.delete_task(task_id)
        except:
            print(f"Warning: Could not clean up test task {task_id}")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            pytest.skip("API key doesn't have sufficient permissions for task operations")
        raise


def test_update_task(tasks_api, test_task_data):
    """Test updating a task."""
    try:
        # Create a task
        task_id, _ = create_test_task(tasks_api, test_task_data)
        
        if not task_id:
            pytest.skip("Could not create test task")
        
        # Generate new data for update
        updated_name = f"Updated Task {uuid.uuid4().hex[:8]}"
        
        # Update the task
        update_data = {
            "name": updated_name,
            "isCompleted": 1  # Use isCompleted instead of status
        }
        
        update_response = tasks_api.update_task(task_id, update_data)
        
        # Debug output
        print("\n\nUpdate Task Response:")
        print(json.dumps(update_response, indent=2))
        
        # Verify update was successful
        assert isinstance(update_response, dict)
        assert "id" in update_response
        assert update_response["id"] == task_id
        assert "name" in update_response
        assert update_response["name"] == updated_name
        assert "isCompleted" in update_response
        assert update_response["isCompleted"] == 1
        
        # Clean up - delete the task
        try:
            tasks_api.delete_task(task_id)
        except:
            print(f"Warning: Could not clean up test task {task_id}")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            pytest.skip("API key doesn't have sufficient permissions for task operations")
        raise


def test_delete_task(tasks_api, test_task_data):
    """Test deleting a task."""
    try:
        # Create a task
        task_id, _ = create_test_task(tasks_api, test_task_data)
        
        if not task_id:
            pytest.skip("Could not create test task")
        
        # Delete the task
        delete_response = tasks_api.delete_task(task_id)
        
        # Debug output
        print("\n\nDelete Task Response:")
        print(delete_response)
        
        # Try to retrieve the deleted task - should fail with 404
        with pytest.raises(FollowUpBossApiException) as excinfo:
            tasks_api.retrieve_task(task_id)
            
        # Verify it's a 404 error
        assert excinfo.value.status_code == 404
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            pytest.skip("API key doesn't have sufficient permissions for task operations")
        raise


def test_retrieve_nonexistent_task(tasks_api):
    """Test retrieving a task that doesn't exist."""
    # Use a very high ID that is unlikely to exist
    nonexistent_id = 99999999
    
    # Attempt to retrieve the task, expect a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        tasks_api.retrieve_task(nonexistent_id)
    
    # Verify it's a 404 error
    assert excinfo.value.status_code == 404
    print(f"Received expected 404 error: {excinfo.value}") 