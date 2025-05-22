"""
Test the Identity API.
"""

import pytest
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.identity import Identity
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
def identity(client):
    """Create an Identity instance for testing."""
    return Identity(client)

def test_get_identity(identity):
    """Test getting identity information."""
    response = identity.get_identity()
    
    # Print response for debugging
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "account" in response
    assert "user" in response
    
    # Check account data
    assert "id" in response["account"]
    assert "name" in response["account"]
    
    # Check user data
    assert "id" in response["user"]
    assert "email" in response["user"] 