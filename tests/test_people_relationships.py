import os

import pytest
from dotenv import load_dotenv

from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.people import People
from follow_up_boss.people_relationships import PeopleRelationships

# Load environment variables from .env file
load_dotenv()


# Test fixtures
@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
    x_system = os.getenv("X_SYSTEM")
    x_system_key = os.getenv("X_SYSTEM_KEY")
    return FollowUpBossApiClient(
        api_key=api_key, x_system=x_system, x_system_key=x_system_key
    )


@pytest.fixture
def people_relationships(client):
    """Create a PeopleRelationships instance for testing."""
    return PeopleRelationships(client)


@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)


@pytest.fixture
def get_test_people_ids(people_api):
    """Get two person IDs for relationship testing."""
    # Get two different people from the API to establish a relationship
    people_response = people_api.list_people(params={"limit": 2})

    # Check if we have enough people for testing
    if "people" not in people_response or len(people_response["people"]) < 2:
        pytest.skip("Not enough people in the account to test relationships")

    # Return the IDs of the first two people
    return people_response["people"][0]["id"], people_response["people"][1]["id"]


def test_list_people_relationships(people_relationships):
    """Test listing people relationships."""
    # Simple test to verify the endpoint functions
    response = people_relationships.list_people_relationships()

    # Verify the response structure based on the actual API response
    assert "_metadata" in response
    assert "peoplerelationships" in response

    # Check metadata structure
    assert "collection" in response["_metadata"]
    assert response["_metadata"]["collection"] == "peoplerelationships"

    # The response should include items and limit in metadata
    assert isinstance(response["peoplerelationships"], list)
    assert "limit" in response["_metadata"]


def test_create_people_relationship(people_relationships, get_test_people_ids):
    """Test creating and manipulating a people relationship."""
    person_id, _ = get_test_people_ids  # We only need one person ID

    # Create a relationship
    response = people_relationships.create_people_relationship(person_id, "Spouse")

    # Verify the response structure
    assert "id" in response
    relationship_id = response["id"]
    assert "type" in response
    assert response["type"] == "Spouse"
    assert "personId" in response
    assert response["personId"] == person_id

    # Retrieve the relationship
    retrieve_response = people_relationships.retrieve_people_relationship(
        relationship_id
    )
    assert retrieve_response["id"] == relationship_id

    # Update the relationship
    update_response = people_relationships.update_people_relationship(
        relationship_id, "Friend"
    )
    assert update_response["type"] == "Friend"

    # Delete the relationship
    delete_response = people_relationships.delete_people_relationship(relationship_id)

    # Verify it's deleted
    with pytest.raises(FollowUpBossApiException) as excinfo:
        people_relationships.retrieve_people_relationship(relationship_id)
    assert excinfo.value.status_code in [404, 400]
