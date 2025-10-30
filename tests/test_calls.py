"""

Test the Calls API.
"""

import datetime
import os
import uuid

import pytest

from follow_up_boss.calls import Calls
from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.people import People

pytestmark = pytest.mark.integration  # Mark all tests in this module as integration


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def calls_api(client):
    """Create a Calls instance for testing."""
    return Calls(client)


@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)


def get_test_person_id(people_api, resource_tracker=None):
    """Create a test person and return their ID."""
    # Generate unique data to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"calls_test_person_{unique_suffix}@example.com"
    first_name = "CallsTest"
    last_name = f"Person{unique_suffix}"

    # Create the person with a phone number for call testing
    person_data = {
        "firstName": first_name,
        "lastName": last_name,
        "emails": [{"value": email, "type": "work"}],
        "phones": [{"value": "555-987-6543", "type": "mobile"}],
    }

    response = people_api.create_person(person_data)
    person_id = response["id"]

    # Track for cleanup if tracker provided
    if resource_tracker is not None:
        resource_tracker["people"].append(person_id)

    return person_id, "555-987-6543"


def create_test_call(calls_api, people_api, resource_tracker=None):
    """Helper function to create a test call and return its ID."""
    # Create a test person
    person_id, phone = get_test_person_id(people_api, resource_tracker)

    # Create call data
    duration = 120  # 2 minutes in seconds
    note = f"This is a test call created at {datetime.datetime.now().isoformat()}"

    # Create the call
    response = calls_api.create_call(
        person_id=person_id,
        phone=phone,
        duration=duration,
        outcome="Left Message",
        is_incoming=False,
        note=note,
    )

    call_id = response["id"]

    # Track for cleanup if tracker provided
    if resource_tracker is not None:
        resource_tracker["calls"].append(call_id)

    return call_id


def test_list_calls(calls_api):
    """Test listing calls."""
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    response = calls_api.list_calls(**params)

    # Debug print
    print("Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "_metadata" in response
    assert "calls" in response

    # Check metadata
    assert "collection" in response["_metadata"]
    assert response["_metadata"]["collection"] == "calls"

    # Check calls data (might be empty in test account)
    assert isinstance(response["calls"], list)


def test_create_call(calls_api, people_api, resource_tracker):
    """Test creating a call for a person."""
    # Create a test person to associate the call with
    person_id, phone = get_test_person_id(people_api, resource_tracker)

    # Create call data
    duration = 120  # 2 minutes in seconds
    note = f"This is a test call created at {datetime.datetime.now().isoformat()}"

    # Valid outcomes from error message: "Interested", "Not Interested", "Left Message", "No Answer", "Busy", "Bad Number"
    response = calls_api.create_call(
        person_id=person_id,
        phone=phone,
        duration=duration,
        outcome="Left Message",  # Valid call outcome from the API
        is_incoming=False,  # Outgoing call
        note=note,
    )

    # Track for cleanup
    resource_tracker["calls"].append(response["id"])

    # Debug print
    print(f"Create Call Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "id" in response
    assert "personId" in response
    assert "outcome" in response
    assert response["personId"] == person_id
    assert response["outcome"] == "Left Message"


def test_retrieve_call(calls_api, people_api, resource_tracker):
    """Test retrieving a specific call."""
    # Create a test call to retrieve
    call_id = create_test_call(calls_api, people_api, resource_tracker)

    # Retrieve the call
    response = calls_api.retrieve_call(call_id)

    # Debug print
    print(f"Retrieve Call {call_id} Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "id" in response
    assert response["id"] == call_id
    assert "personId" in response
    assert "outcome" in response


def test_update_call(calls_api, people_api, resource_tracker):
    """Test updating a call."""
    # Create a test call to update
    call_id = create_test_call(calls_api, people_api, resource_tracker)

    # Get original call to see what we can update
    original_call = calls_api.retrieve_call(call_id)
    print(f"Original Call:", original_call)

    # Update data - change outcome and duration
    update_data = {
        "outcome": "Interested",  # Change from "Left Message" to "Interested"
        "duration": 180,  # Change from 120 to 180 seconds
    }

    # Update the call
    response = calls_api.update_call(call_id, update_data)

    # Debug print
    print(f"Update Call {call_id} Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "id" in response
    assert response["id"] == call_id
    assert "outcome" in response
    assert "duration" in response
    assert response["outcome"] == "Interested"
    assert response["duration"] == 180
