"""
Test the Deals API.
"""

import pytest
import os
from datetime import datetime, timedelta
from follow_up_boss_api.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss_api.deals import Deals
from follow_up_boss_api.pipelines import Pipelines
from follow_up_boss_api.stages import Stages
from follow_up_boss_api.users import Users
from follow_up_boss_api.people import People

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )

@pytest.fixture
def deals_api(client):
    """Create a Deals instance for testing."""
    return Deals(client)

@pytest.fixture
def pipelines_api(client):
    """Create a Pipelines instance for testing."""
    return Pipelines(client)

@pytest.fixture
def stages_api(client):
    """Create a Stages instance for testing."""
    return Stages(client)

@pytest.fixture
def users_api(client):
    """Create a Users instance for testing."""
    return Users(client)

@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

@pytest.fixture
def test_pipeline_id(pipelines_api):
    """Get a pipeline ID for testing or create one if needed."""
    # Get a pipeline
    pipelines_response = pipelines_api.list_pipelines()
    
    pipeline_id = None
    if 'pipelines' in pipelines_response and pipelines_response['pipelines']:
        pipeline_id = pipelines_response['pipelines'][0]['id']
    else:
        # Create a pipeline if none exists
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_pipeline = pipelines_api.create_pipeline(
            name=f"Test Pipeline {timestamp}"
        )
        pipeline_id = new_pipeline['id']
    
    return pipeline_id

@pytest.fixture
def test_stage_id(pipelines_api, test_pipeline_id):
    """Get a stage ID for testing that belongs to the pipeline."""
    # Get the pipeline to find its stages
    pipeline_response = pipelines_api.retrieve_pipeline(test_pipeline_id)
    
    if 'stages' not in pipeline_response or not pipeline_response['stages']:
        # If the pipeline has no stages, we'll get stages from the general stages endpoint
        # but this will likely fail as the stage needs to be part of the pipeline
        stages_response = pipelines_api.list_pipelines()
        for pipeline in stages_response.get('pipelines', []):
            if pipeline.get('id') == test_pipeline_id and pipeline.get('stages'):
                return pipeline['stages'][0]['id']
        
        pytest.skip("No stages available for the selected pipeline")
    
    # Return the first stage in the pipeline
    return pipeline_response['stages'][0]['id']

@pytest.fixture
def test_user_id(users_api):
    """Get a user ID for testing."""
    # Get a user
    users_response = users_api.list_users()
    
    if 'users' not in users_response or not users_response['users']:
        pytest.skip("No users available for testing")
    
    return users_response['users'][0]['id']

@pytest.fixture
def test_person_id(people_api):
    """Get a person ID for testing."""
    # Get a person
    people_response = people_api.list_people(params={"limit": 1})
    
    if 'people' not in people_response or not people_response['people']:
        pytest.skip("No people available for testing")
    
    return people_response['people'][0]['id']

@pytest.fixture
def test_deal_id(deals_api, test_stage_id):
    """Create a test deal and return its ID for testing."""
    # Create a minimal deal with just stageId which is the only required field
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    deal_data = {
        "name": f"Test Deal {timestamp}",
        "stage_id": test_stage_id
    }
    
    try:
        response = deals_api.create_deal(**deal_data)
        deal_id = response['id']
        
        yield deal_id
        
        # Clean up the deal after test
        try:
            deals_api.delete_deal(deal_id)
        except Exception as e:
            print(f"Error cleaning up test deal: {e}")
    except FollowUpBossApiException as e:
        pytest.skip(f"Failed to create test deal: {e}")

def test_list_deals(deals_api):
    """Test listing deals."""
    response = deals_api.list_deals()
    
    # Debug info
    print(f"List deals response: {response}")
    
    # Verify response structure
    assert isinstance(response, dict)
    # The response should contain a list of deals - the exact key might vary
    found_deals = False
    for key in ['deals', 'data', '_data']:
        if key in response and isinstance(response[key], list):
            found_deals = True
            break
    
    # Should have a metadata section
    assert '_metadata' in response
    
    # Either found deals key or it's in metadata
    assert found_deals or 'collection' in response['_metadata']

def test_create_and_retrieve_deal(deals_api, test_stage_id):
    """Test creating and retrieving a deal."""
    # Create a minimal deal
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    deal_name = f"Test Deal {timestamp}"
    
    response = deals_api.create_deal(
        name=deal_name,
        stage_id=test_stage_id
    )
    
    # Debug info
    print(f"Create deal response: {response}")
    
    # Verify the deal was created successfully
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['name'] == deal_name
    
    deal_id = response['id']
    
    # Retrieve the deal
    retrieve_response = deals_api.retrieve_deal(deal_id)
    
    # Debug info
    print(f"Retrieve deal response: {retrieve_response}")
    
    # Verify the retrieved deal matches what we created
    assert isinstance(retrieve_response, dict)
    assert retrieve_response['id'] == deal_id
    assert retrieve_response['name'] == deal_name
    
    # Clean up
    deals_api.delete_deal(deal_id)

def test_update_deal(deals_api, test_deal_id):
    """Test updating a deal."""
    # Update the deal
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    updated_name = f"Updated Deal {timestamp}"
    updated_price = 150000.00
    
    update_data = {
        "name": updated_name,
        "price": updated_price
    }
    
    response = deals_api.update_deal(test_deal_id, update_data)
    
    # Debug info
    print(f"Update deal response: {response}")
    
    # Verify the deal was updated successfully
    assert isinstance(response, dict)
    assert response['id'] == test_deal_id
    assert response['name'] == updated_name
    assert abs(float(response['price']) - updated_price) < 0.01  # Handle potential floating point differences
    
    # Retrieve the deal to verify updates
    retrieve_response = deals_api.retrieve_deal(test_deal_id)
    
    # Verify the retrieved deal has the updates
    assert retrieve_response['name'] == updated_name
    assert abs(float(retrieve_response['price']) - updated_price) < 0.01

def test_delete_deal(deals_api, test_stage_id):
    """Test deleting a deal."""
    # Create a deal specifically for deletion with minimal fields
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    deal_name = f"Delete Test Deal {timestamp}"
    
    response = deals_api.create_deal(
        name=deal_name,
        stage_id=test_stage_id
    )
    
    # Verify the deal was created
    assert 'id' in response
    deal_id = response['id']
    
    # Delete the deal
    delete_response = deals_api.delete_deal(deal_id)
    
    # Debug info
    print(f"Delete deal response: {delete_response}")
    
    # Verify deletion - the API returns an empty list for successful deletion
    assert delete_response == "" or delete_response == [] or (isinstance(delete_response, dict) and not delete_response)
    
    # The API marks deals as "Deleted" rather than actually removing them
    # Retrieve the deal to verify its status
    retrieve_response = deals_api.retrieve_deal(deal_id)
    
    # Verify the deal has been marked as deleted
    assert retrieve_response['status'] == 'Deleted' 