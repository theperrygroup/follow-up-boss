"""
Test the Smart Lists API.
"""

import pytest
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.smart_lists import SmartLists
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
def smart_lists_api(client):
    """Create a SmartLists instance for testing."""
    return SmartLists(client)

def test_list_smart_lists(smart_lists_api):
    """Test listing smart lists."""
    response = smart_lists_api.list_smart_lists()
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    assert 'smartlists' in response
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'smartlists'
    
    # Check smart lists data
    assert isinstance(response['smartlists'], list)
    
    # Verify that the response is valid
    assert response is not None
    print(f"Successfully listed {len(response['smartlists'])} smart lists")

def test_retrieve_smart_list(smart_lists_api):
    """Test retrieving a specific smart list."""
    # First, get a list of smart lists to find a valid ID
    list_response = smart_lists_api.list_smart_lists()
    
    # Make sure we have at least one smart list
    if not list_response['smartlists']:
        pytest.skip("No smart lists available to test retrieving a specific one")
    
    # Get the ID of the first smart list
    smart_list_id = list_response['smartlists'][0]['id']
    
    # Now retrieve that specific smart list
    response = smart_lists_api.retrieve_smart_list(smart_list_id)
    
    # Debug print
    print(f"Smart List {smart_list_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == smart_list_id  # Make sure we got the right smart list
    assert 'name' in response 