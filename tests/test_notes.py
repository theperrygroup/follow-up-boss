"""
Test the Notes API.
"""

import pytest
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.notes import Notes
from follow_up_boss_api.people import People
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
def notes_api(client):
    """Create a Notes instance for testing."""
    return Notes(client)

@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

def get_test_person_id(people_api):
    """Create a test person and return their ID."""
    # Generate unique data to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"note_test_person_{unique_suffix}@example.com"
    first_name = "NoteTest"
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

def create_test_note(notes_api, people_api):
    """Helper function to create a test note and return its ID."""
    # Create a test person to associate the note with
    person_id = get_test_person_id(people_api)
    
    # Generate unique content for the note
    subject = f"Test Note {uuid.uuid4().hex[:6]}"
    body = f"This is a test note created at {uuid.uuid4().hex}"
    
    # Create the note
    response = notes_api.create_note(person_id, subject, body)
    return response['id'], subject, body

def test_list_notes(notes_api):
    """Test listing notes."""
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    response = notes_api.list_notes(params=params)
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    assert 'notes' in response
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'notes'
    
    # Check notes data
    assert isinstance(response['notes'], list)

def test_create_note(notes_api, people_api):
    """Test creating a note for a person."""
    # Create a test person to associate the note with
    person_id = get_test_person_id(people_api)
    
    # Generate unique content for the note
    subject = f"Test Note {uuid.uuid4().hex[:6]}"
    body = f"This is a test note created at {uuid.uuid4().hex}"
    
    # Create the note
    response = notes_api.create_note(person_id, subject, body)
    
    # Debug print
    print(f"Create Note Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert 'subject' in response
    assert 'body' in response
    assert 'personId' in response
    assert response['subject'] == subject
    assert response['body'] == body
    assert response['personId'] == person_id

def test_retrieve_note(notes_api, people_api):
    """Test retrieving a specific note."""
    # Create a test note to retrieve
    note_id, subject, body = create_test_note(notes_api, people_api)
    
    # Retrieve the note
    response = notes_api.retrieve_note(note_id)
    
    # Debug print
    print(f"Retrieve Note {note_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == note_id
    assert 'subject' in response
    assert response['subject'] == subject
    assert 'body' in response
    assert response['body'] == body

def test_update_note(notes_api, people_api):
    """Test updating a note."""
    # Create a test note to update
    note_id, _, _ = create_test_note(notes_api, people_api)
    
    # Generate new content for the update
    new_subject = f"Updated Note {uuid.uuid4().hex[:6]}"
    new_body = f"This note was updated at {uuid.uuid4().hex}"
    
    # Update the note
    response = notes_api.update_note(note_id, subject=new_subject, body=new_body)
    
    # Debug print
    print(f"Update Note {note_id} Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert 'id' in response
    assert response['id'] == note_id
    assert 'subject' in response
    assert response['subject'] == new_subject
    assert 'body' in response
    assert response['body'] == new_body

def test_delete_note(notes_api, people_api):
    """Test deleting a note."""
    # Create a test note to delete
    note_id, _, _ = create_test_note(notes_api, people_api)
    
    # Delete the note
    response = notes_api.delete_note(note_id)
    
    # Debug print
    print(f"Delete Note {note_id} Response:", response)
    
    # For successful deletion, the response is typically empty (or a success message)
    # The key test is that we don't get an error
    
    # Try to retrieve the deleted note - should fail
    with pytest.raises(Exception) as excinfo:
        notes_api.retrieve_note(note_id)
    
    # Debug print
    print(f"Attempting to retrieve deleted note exception:", excinfo.value) 