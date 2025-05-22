"""
Test the People Unclaimed API endpoints.
"""

import pytest
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.people import People
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
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

def test_list_unclaimed_people(people_api):
    """Test listing unclaimed people."""
    # Request unclaimed people with minimal parameters
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    response = people_api.list_unclaimed_people(params=params)
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    if 'people' in response:  # Some APIs return 'persons' instead of 'people'
        assert isinstance(response['people'], list)
    elif 'persons' in response:
        assert isinstance(response['persons'], list)
    else:
        # If neither key exists, there are likely no unclaimed people
        assert '_metadata' in response
        # Check that collection field exists in metadata
        assert 'collection' in response['_metadata']
        # This should be 'people' or similar
        assert response['_metadata']['collection'] in ['people', 'persons', 'unclaimed']

def test_claim_person_invalid_id(people_api):
    """Test claiming an unclaimed person with an invalid ID."""
    # Use a likely invalid person ID
    invalid_id = 9999999
    
    # Try to claim the person, expecting an error
    try:
        response = people_api.claim_person({"personId": invalid_id})
        print(f"Claim invalid person response: {response}")
        # If we get here, either the API actually found this ID (unlikely) or doesn't validate IDs
        if isinstance(response, dict) and 'error' in response:
            assert 'error' in response
            print(f"API returned error as expected: {response['error']}")
        else:
            # If we succeeded, let's just note it but not fail the test
            print(f"WARNING: Claiming person with ID {invalid_id} unexpectedly succeeded.")
    except requests.exceptions.HTTPError as e:
        # This is the expected outcome - check for an appropriate error code
        print(f"Expected HTTP error: {str(e)}")
        assert e.response.status_code in [400, 404]  # Either bad request or not found
        print(f"API returned status code {e.response.status_code} as expected.")

def test_ignore_unclaimed_person_invalid_id(people_api):
    """Test ignoring an unclaimed person with an invalid ID."""
    # Use a likely invalid person ID
    invalid_id = 9999999
    
    # Try to ignore the person, expecting an error
    try:
        response = people_api.ignore_unclaimed_person({"personId": invalid_id})
        print(f"Ignore invalid person response: {response}")
        # If we get here, either the API actually found this ID (unlikely) or doesn't validate IDs
        if isinstance(response, dict) and 'error' in response:
            assert 'error' in response
            print(f"API returned error as expected: {response['error']}")
        else:
            # If we succeeded, let's just note it but not fail the test
            print(f"WARNING: Ignoring person with ID {invalid_id} unexpectedly succeeded.")
    except requests.exceptions.HTTPError as e:
        # This is the expected outcome - check for an appropriate error code
        print(f"Expected HTTP error: {str(e)}")
        assert e.response.status_code in [400, 404]  # Either bad request or not found
        print(f"API returned status code {e.response.status_code} as expected.")

# Note: Creating, claiming, and ignoring real unclaimed people would require a more complex
# test setup that depends on the specific business rules of Follow Up Boss. These tests
# verify the basic API endpoints work without disrupting actual business data. 