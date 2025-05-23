"""
Test the Action Plans API.
"""

import pytest
import uuid
from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.action_plans import ActionPlans
from follow_up_boss.people import People
import os
import requests

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )

@pytest.fixture
def action_plans_api(client):
    """Create an ActionPlans instance for testing."""
    return ActionPlans(client)

@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

def create_test_person(people_api):
    """Create a test person and return their ID."""
    # Generate unique data to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"action_plan_test_{unique_suffix}@example.com"
    first_name = "ActionTest"
    last_name = f"Person{unique_suffix}"
    
    # Create the person
    person_data = {
        "firstName": first_name,
        "lastName": last_name,
        "emails": [
            {
                "value": email,
                "type": "work"
            }
        ]
    }
    
    response = people_api.create_person(person_data)
    return response['id']

def test_list_action_plans(action_plans_api):
    """Test listing action plans."""
    # List action plans
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    try:
        response = action_plans_api.list_action_plans(**params)
        
        # Debug print
        print("Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert '_metadata' in response
        
        # The API might return 'actionPlans' or 'plans' key
        if 'actionPlans' in response:
            assert isinstance(response['actionPlans'], list)
        elif 'plans' in response:
            assert isinstance(response['plans'], list)
        else:
            # If neither key exists, check metadata for expected collection name
            assert 'collection' in response['_metadata']
            expected_collections = ['actionPlans', 'plans']
            assert response['_metadata']['collection'] in expected_collections
    except FollowUpBossApiException as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.status_code == 403:
            pytest.skip(f"API key doesn't have access to Action Plans: {str(e)}")
        else:
            raise

def test_list_action_plan_assignments(action_plans_api):
    """Test listing action plan assignments."""
    # List action plan assignments
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    try:
        response = action_plans_api.list_action_plan_assignments(**params)
        
        # Debug print
        print("Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert '_metadata' in response
        
        # The API might return different key names for the assignments
        collection_keys = ['actionPlansPeople', 'assignments', 'people']
        found_key = False
        for key in collection_keys:
            if key in response:
                assert isinstance(response[key], list)
                found_key = True
                break
        
        # If none of the expected keys exist, check metadata
        if not found_key:
            assert 'collection' in response['_metadata']
            expected_collections = ['actionPlansPeople', 'assignments', 'people']
            assert response['_metadata']['collection'] in expected_collections
    except FollowUpBossApiException as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.status_code == 403:
            pytest.skip(f"API key doesn't have access to Action Plan Assignments: {str(e)}")
        else:
            raise

def test_assign_person_to_action_plan_invalid_ids(action_plans_api, people_api):
    """Test assigning a person to an action plan with invalid IDs."""
    # First, create a real person to test with
    person_id = create_test_person(people_api)
    
    # Use an invalid action plan ID
    invalid_action_plan_id = 9999999
    
    # Try to assign the person to the invalid action plan
    with pytest.raises(FollowUpBossApiException) as excinfo:
        response = action_plans_api.assign_person_to_action_plan(
            person_id=person_id,
            action_plan_id=invalid_action_plan_id
        )
    
    # This is the expected outcome for invalid IDs
    print(f"Expected API exception: {str(excinfo.value)}")
    assert excinfo.value.status_code in [400, 404]  # Either bad request or not found
    print(f"API returned status code {excinfo.value.status_code} as expected")

def test_update_action_plan_assignment_invalid_id(action_plans_api):
    """Test updating an action plan assignment with an invalid ID."""
    # Use an invalid assignment ID
    invalid_assignment_id = 9999999
    
    # Try to update the assignment with the invalid ID
    with pytest.raises(FollowUpBossApiException) as excinfo:
        update_data = {"status": "Paused"}
        response = action_plans_api.update_action_plan_assignment(
            assignment_id=invalid_assignment_id,
            update_data=update_data
        )
    
    # Expected outcome for invalid IDs
    print(f"Expected API exception: {str(excinfo.value)}")
    assert excinfo.value.status_code in [400, 404]  # Either bad request or not found
    print(f"API returned status code {excinfo.value.status_code} as expected") 