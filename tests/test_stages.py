"""
Test the Stages API.
"""

import os
import uuid

import pytest

from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.pipelines import Pipelines
from follow_up_boss.stages import Stages


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def stages_api(client):
    """Create a Stages instance for testing."""
    return Stages(client)


@pytest.fixture
def pipelines_api(client):
    """Create a Pipelines instance for testing."""
    return Pipelines(client)


def create_test_pipeline(pipelines_api):
    """Helper function to create a test pipeline for stages testing."""
    # Generate a unique name
    unique_suffix = uuid.uuid4().hex[:8]
    name = f"Test Pipeline {unique_suffix}"

    # Create the pipeline
    response = pipelines_api.create_pipeline(name=name)
    assert "id" in response, "Pipeline creation failed"
    return response["id"]


def test_list_stages(stages_api):
    """Test listing stages."""
    response = stages_api.list_stages()

    # Debug print
    print("List Stages Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "_metadata" in response

    # The API might return 'stages' or similar key
    if "stages" in response:
        assert isinstance(response["stages"], list)
    else:
        # Check metadata for collection name
        assert "collection" in response["_metadata"]
        assert response["_metadata"]["collection"] in ["stages"]


def test_create_and_retrieve_stage(stages_api):
    """Test creating and then retrieving a stage."""
    # Generate a unique name for the stage
    unique_suffix = uuid.uuid4().hex[:8]
    stage_name = f"Test Stage {unique_suffix}"

    # Create the stage without pipeline_id since API is rejecting this field
    create_response = stages_api.create_stage(name=stage_name)

    # Debug print
    print("Create Stage Response:", create_response)

    # Check that the stage was created successfully
    assert isinstance(create_response, dict)
    assert "id" in create_response
    assert "name" in create_response
    assert create_response["name"] == stage_name

    # Retrieve the stage to verify it exists
    stage_id = create_response["id"]
    retrieve_response = stages_api.retrieve_stage(stage_id)

    # Debug print
    print("Retrieve Stage Response:", retrieve_response)

    # Verify the retrieved stage matches what we created
    assert isinstance(retrieve_response, dict)
    assert "id" in retrieve_response
    assert retrieve_response["id"] == stage_id
    assert "name" in retrieve_response
    assert retrieve_response["name"] == stage_name

    # Clean up - delete the stage
    try:
        # Get another stage ID to reassign to (required for deletion)
        stages_response = stages_api.list_stages()
        other_stages = [
            stage
            for stage in stages_response.get("stages", [])
            if stage["id"] != stage_id
        ]

        if other_stages:
            # Use another stage for reassignment
            assign_stage_id = other_stages[0]["id"]
            stages_api.delete_stage(stage_id, assign_stage_id=assign_stage_id)
        else:
            # Skip deletion test if no other stage is available
            print("Skipping stage deletion - no other stage available for reassignment")
    except Exception as e:
        print(f"Note: Failed to clean up test stage {stage_id}: {str(e)}")


def test_update_stage(stages_api):
    """Test updating a stage."""
    # Generate names
    original_name = f"Original Stage {uuid.uuid4().hex[:8]}"
    updated_name = f"Updated Stage {uuid.uuid4().hex[:8]}"

    # Create the stage without pipeline_id
    create_response = stages_api.create_stage(name=original_name)

    stage_id = create_response["id"]

    # Update the stage
    update_data = {"name": updated_name}
    update_response = stages_api.update_stage(stage_id, update_data)

    # Debug print
    print("Update Stage Response:", update_response)

    # Check that the stage was updated correctly
    assert isinstance(update_response, dict)
    assert "id" in update_response
    assert update_response["id"] == stage_id
    assert "name" in update_response
    assert update_response["name"] == updated_name

    # Clean up - delete the stage
    try:
        # Get another stage ID to reassign to (required for deletion)
        stages_response = stages_api.list_stages()
        other_stages = [
            stage
            for stage in stages_response.get("stages", [])
            if stage["id"] != stage_id
        ]

        if other_stages:
            # Use another stage for reassignment
            assign_stage_id = other_stages[0]["id"]
            stages_api.delete_stage(stage_id, assign_stage_id=assign_stage_id)
        else:
            # Skip deletion test if no other stage is available
            print("Skipping stage deletion - no other stage available for reassignment")
    except Exception as e:
        print(f"Note: Failed to clean up test stage {stage_id}: {str(e)}")


def test_retrieve_nonexistent_stage(stages_api):
    """Test retrieving a stage that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999

    # Try to retrieve the stage, expecting a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        stages_api.retrieve_stage(nonexistent_id)

    # Check that it's a 404 error
    assert excinfo.value.status_code in [404, 400]  # Either not found or bad request
    print(f"Received expected error: {excinfo.value}")
