import os
import pytest
from dotenv import load_dotenv
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.people_relationships import PeopleRelationships

# Load environment variables from .env file
load_dotenv()

# Test fixtures
@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
    x_system = os.getenv("X_SYSTEM")
    x_system_key = os.getenv("X_SYSTEM_KEY")
    return FollowUpBossApiClient(api_key=api_key, x_system=x_system, x_system_key=x_system_key)

@pytest.fixture
def people_relationships(client):
    """Create a PeopleRelationships instance for testing."""
    return PeopleRelationships(client)

def test_list_people_relationships(people_relationships):
    """Test listing people relationships."""
    # Simple test to verify the endpoint functions
    response = people_relationships.list_people_relationships()
    
    # Verify the response structure based on the actual API response
    assert '_metadata' in response
    assert 'peoplerelationships' in response
    
    # Check metadata structure
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'peoplerelationships'
    
    # The response should include items and limit in metadata
    assert isinstance(response['peoplerelationships'], list)
    assert 'limit' in response['_metadata'] 