"""
Test the Users API.
"""

import pytest
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.users import Users
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
def users_api(client):
    """Create a Users instance for testing."""
    return Users(client)

def test_list_users(users_api):
    """Test listing users."""
    response = users_api.list_users()
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    assert 'users' in response
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'users'
    
    # Check users data
    assert isinstance(response['users'], list)
    assert len(response['users']) > 0  # Should have at least one user
    
    # Check structure of the first user
    first_user = response['users'][0]
    assert 'id' in first_user
    assert 'email' in first_user

def test_retrieve_user(users_api):
    """Test retrieving a specific user."""
    # First, get a list of users to find a valid ID
    users_response = users_api.list_users()
    user_id = users_response['users'][0]['id']
    
    # Now retrieve that specific user
    response = users_api.retrieve_user(user_id)
    
    # Debug print
    print(f"User {user_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == user_id  # Make sure we got the right user
    assert 'email' in response

def test_get_current_user(users_api):
    """Test retrieving the current user."""
    response = users_api.get_current_user()
    
    # Debug print
    print("Me Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert 'email' in response 