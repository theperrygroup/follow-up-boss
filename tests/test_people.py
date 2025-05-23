"""
Test the People API.
"""

import pytest
import uuid
import requests
from follow_up_boss.client import FollowUpBossApiException
from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.people import People
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
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

def get_test_people(people_api):
    """Helper function to get test people data."""
    # Use a params dictionary instead of keyword arguments
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    response = people_api.list_people(params=params)
    return response

def test_list_people(people_api):
    """Test listing people."""
    response = get_test_people(people_api)
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    assert 'people' in response
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'people'
    
    # Check people data (might be empty in test account)
    assert isinstance(response['people'], list)

def test_retrieve_person(people_api):
    """Test retrieving a specific person."""
    # First, get a list of people to find a valid ID
    list_response = get_test_people(people_api)
    
    # Make sure we have at least one person
    if not list_response['people']:
        pytest.skip("No people available to test retrieving a specific one")
    
    # Get the ID of the first person
    person_id = list_response['people'][0]['id']
    
    # Now retrieve that specific person
    response = people_api.retrieve_person(person_id)
    
    # Debug print
    print(f"Person {person_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == person_id  # Make sure we got the right person
    assert 'name' in response

def create_test_person(people_api):
    """Helper function to create a test person for deletion."""
    # Generate unique data to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"delete_test_person_{unique_suffix}@example.com"
    first_name = "DeleteTest"
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

def test_create_person(people_api):
    """Test creating a new person."""
    # Generate unique data to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"test_person_{unique_suffix}@example.com"
    first_name = "Test"
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
    
    # Debug print
    print(f"Create Person Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert 'firstName' in response
    assert 'lastName' in response
    assert response['firstName'] == first_name
    assert response['lastName'] == last_name
    
    # Check that the email was created
    assert 'emails' in response
    assert isinstance(response['emails'], list)
    assert any(e['value'] == email for e in response['emails'])
    
    # Verify that we got a valid person ID
    assert isinstance(response['id'], int)
    assert response['id'] > 0
    print(f"Person created successfully with ID: {response['id']}")

def test_update_person(people_api):
    """Test updating a person."""
    # First, create a person to update using the helper function
    person_id = create_test_person(people_api)
    
    # Generate a new unique name for the update
    new_last_name = f"UpdatedPerson{uuid.uuid4().hex[:6]}"
    
    # Update data
    update_data = {
        "lastName": new_last_name
    }
    
    # Update the person
    response = people_api.update_person(person_id, update_data)
    
    # Debug print
    print(f"Update Person {person_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == person_id
    assert 'lastName' in response
    assert response['lastName'] == new_last_name

def test_delete_person(people_api):
    """Test deleting a person."""
    # Create a test person to delete
    person_id = create_test_person(people_api)
    
    # Delete the person
    response = people_api.delete_person(person_id)
    
    # Debug print
    print(f"Delete Person {person_id} Response:", response)
    
    # For successful deletion, the response is typically empty or a success message
    # The key test is that we don't get an error
    
    # Try to retrieve the deleted person - should fail with a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        people_api.retrieve_person(person_id)
    
    # Check that it's a 404 error
    assert "404 Client Error" in str(excinfo.value)
    print(f"Attempting to retrieve deleted person exception:", excinfo.value)

def test_check_duplicate(people_api):
    """Test checking for duplicate people."""
    # Create a person to check for duplicates
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"duplicate_test_person_{unique_suffix}@example.com"
    phone = "555-123-4567"
    
    # Create the person with email and phone
    person_data = {
        "firstName": "DuplicateTest",
        "lastName": f"Person{unique_suffix}",
        "emails": [
            {
                "value": email,
                "type": "work"
            }
        ],
        "phones": [
            {
                "value": phone,
                "type": "mobile"
            }
        ]
    }
    
    # Create the person
    created_person = people_api.create_person(person_data)
    person_id = created_person['id']
    
    try:
        # Check for duplicates by email
        response_email = people_api.check_duplicate({"email": email})
        print(f"Check Duplicate by Email Response:", response_email)
        
        # Check basic structure of the response
        assert isinstance(response_email, dict)
        # Check that a duplicate was found
        assert 'found' in response_email
        assert response_email['found'] is True
        # Check that it was matched by email
        assert 'matchedBy' in response_email
        assert response_email['matchedBy'] == 'email'
        
        # Check for duplicates by phone
        response_phone = people_api.check_duplicate({"phone": phone})
        print(f"Check Duplicate by Phone Response:", response_phone)
        
        # Check basic structure of the response
        assert isinstance(response_phone, dict)
        # Check that a duplicate was found
        assert 'found' in response_phone
        assert response_phone['found'] is True
        # Check that it was matched by phone
        assert 'matchedBy' in response_phone
        assert response_phone['matchedBy'] == 'phone'
        
    finally:
        # Clean up - delete the created person
        people_api.delete_person(person_id) 