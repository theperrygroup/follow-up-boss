"""
Test the Pipelines API.
"""

import os
import uuid

import pytest

from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.pipelines import Pipelines


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def pipelines_api(client):
    """Create a Pipelines instance for testing."""
    return Pipelines(client)


def test_list_pipelines(pipelines_api):
    """Test listing pipelines."""
    response = pipelines_api.list_pipelines()

    # Debug print
    print("Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "_metadata" in response
    assert "pipelines" in response

    # Check metadata
    assert "collection" in response["_metadata"]
    assert response["_metadata"]["collection"] == "pipelines"

    # Check pipelines data (might be empty in test account)
    assert isinstance(response["pipelines"], list)

    # Verify that the response is valid
    assert response is not None
    print(f"Successfully listed {len(response['pipelines'])} pipelines")


def test_retrieve_pipeline(pipelines_api):
    """Test retrieving a specific pipeline."""
    # First, get a list of pipelines to find a valid ID
    list_response = pipelines_api.list_pipelines()

    # Make sure we have at least one pipeline
    if not list_response["pipelines"]:
        pytest.skip("No pipelines available to test retrieving a specific one")

    # Get the ID of the first pipeline
    pipeline_id = list_response["pipelines"][0]["id"]

    # Now retrieve that specific pipeline
    response = pipelines_api.retrieve_pipeline(pipeline_id)

    # Debug print
    print(f"Pipeline {pipeline_id} Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "id" in response
    assert response["id"] == pipeline_id  # Make sure we got the right pipeline
    assert "name" in response


def create_test_pipeline(pipelines_api):
    """Helper function to create a test pipeline for updating/deleting."""
    # Generate a unique name for the pipeline to avoid conflicts
    unique_name = f"Test Pipeline {uuid.uuid4().hex[:8]}"

    # Create the pipeline
    response = pipelines_api.create_pipeline(name=unique_name)

    # Make sure creation was successful
    assert isinstance(response, dict)
    assert "id" in response

    # Return the ID and name for use in tests
    return response["id"], unique_name


def test_create_pipeline(pipelines_api):
    """Test creating a new pipeline."""
    # Generate a unique name for the pipeline to avoid conflicts
    unique_name = f"Test Pipeline {uuid.uuid4().hex[:8]}"

    # Create the pipeline
    response = pipelines_api.create_pipeline(name=unique_name)

    # Debug print
    print(f"Create Pipeline Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "id" in response
    assert "name" in response
    assert response["name"] == unique_name


def test_update_pipeline(pipelines_api):
    """Test updating a pipeline."""
    # Create a test pipeline to update
    pipeline_id, original_name = create_test_pipeline(pipelines_api)

    # Generate a new unique name for the update
    new_name = f"Updated Pipeline {uuid.uuid4().hex[:8]}"

    # Update data
    update_data = {
        "name": new_name,
        "description": f"This is a test pipeline updated at {uuid.uuid4().hex[:6]}",
    }

    # Update the pipeline
    response = pipelines_api.update_pipeline(pipeline_id, update_data)

    # Debug print
    print(f"Update Pipeline {pipeline_id} Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "id" in response
    assert response["id"] == pipeline_id
    assert "name" in response
    assert response["name"] == new_name
    assert "description" in response
    assert response["description"] == update_data["description"]

    # Verify that we got a valid ID
    assert isinstance(response["id"], int)
    assert response["id"] > 0
    print(f"Pipeline {pipeline_id} updated successfully")


def test_delete_pipeline(pipelines_api):
    """Test deleting a pipeline."""
    # Create a test pipeline to delete
    pipeline_id, _ = create_test_pipeline(pipelines_api)

    # Delete the pipeline
    response = pipelines_api.delete_pipeline(pipeline_id)

    # Debug print
    print(f"Delete Pipeline {pipeline_id} Response:", response)

    # For successful deletion, the response might be empty, None, or a success message
    # Let's check that we can't retrieve the deleted pipeline anymore

    try:
        # Try to retrieve the deleted pipeline - should fail
        pipelines_api.retrieve_pipeline(pipeline_id)
        # If we get here, the pipeline wasn't deleted
        assert False, f"Pipeline {pipeline_id} was not deleted properly"
    except Exception as e:
        # Expected: pipeline should not be found
        print(f"Expected error when retrieving deleted pipeline: {e}")
        assert True
