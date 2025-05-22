"""
Test the Pipelines API.
"""

import pytest
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.pipelines import Pipelines
import os

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
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
    assert '_metadata' in response
    assert 'pipelines' in response
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'pipelines'
    
    # Check pipelines data (might be empty in test account)
    assert isinstance(response['pipelines'], list)
    
    # Return the data for use in other tests
    return response

def test_retrieve_pipeline(pipelines_api):
    """Test retrieving a specific pipeline."""
    # First, get a list of pipelines to find a valid ID
    list_response = test_list_pipelines(pipelines_api)
    
    # Make sure we have at least one pipeline
    if not list_response['pipelines']:
        pytest.skip("No pipelines available to test retrieving a specific one")
    
    # Get the ID of the first pipeline
    pipeline_id = list_response['pipelines'][0]['id']
    
    # Now retrieve that specific pipeline
    response = pipelines_api.retrieve_pipeline(pipeline_id)
    
    # Debug print
    print(f"Pipeline {pipeline_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == pipeline_id  # Make sure we got the right pipeline
    assert 'name' in response

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
    assert 'id' in response
    assert 'name' in response
    assert response['name'] == unique_name
    
    # Store the ID as a variable but don't return it
    pipeline_id = response['id']
    # We could add cleanup code here if needed 