"""
Test the Text Messages API.
"""

import pytest
import uuid
import datetime
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.text_messages import TextMessages
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
def text_messages_api(client):
    """Create a TextMessages instance for testing."""
    return TextMessages(client)

@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

def get_test_person_id(people_api):
    """Create a test person and return their ID."""
    # Generate unique data to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"text_msg_test_person_{unique_suffix}@example.com"
    first_name = "TextMsgTest"
    last_name = f"Person{unique_suffix}"
    
    # Create the person with a phone number for text message testing
    person_data = {
        "firstName": first_name,
        "lastName": last_name,
        "emails": [
            {
                "value": email,
                "type": "work"
            }
        ],
        "phones": [
            {
                "value": "555-123-4567",
                "type": "mobile"
            }
        ]
    }
    
    response = people_api.create_person(person_data)
    return response['id']

def test_list_text_messages(text_messages_api, people_api):
    """Test listing text messages for a person."""
    # Create a test person
    person_id = get_test_person_id(people_api)
    
    # List text messages for the person
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    response = text_messages_api.list_text_messages(person_id=person_id, **params)
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    assert 'textmessages' in response  # API returns 'textmessages' (lowercase) not 'textMessages'
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'textmessages'
    
    # Check text messages data (likely empty for new test person)
    assert isinstance(response['textmessages'], list)

def test_retrieve_text_message_not_found(text_messages_api):
    """Test retrieving a text message that doesn't exist."""
    # Use a non-existent ID
    non_existent_id = 9999999
    
    # Attempt to retrieve the non-existent text message, expecting a 404
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        text_messages_api.retrieve_text_message(non_existent_id)
    
    # Check that it's a 404 error
    assert "404 Client Error" in str(excinfo.value)
    print(f"Received expected 404 error: {excinfo.value}") 