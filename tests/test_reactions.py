"""
Test the Reactions API.
"""

import pytest
import os
from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.reactions import Reactions
from follow_up_boss.notes import Notes
from follow_up_boss.people import People

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )

@pytest.fixture
def reactions_api(client):
    """Create a Reactions instance for testing."""
    return Reactions(client)

@pytest.fixture
def notes_api(client):
    """Create a Notes instance for testing."""
    return Notes(client)

@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)

@pytest.fixture
def test_person_id(people_api):
    """Get a test person ID."""
    # Get a test person
    people_response = people_api.list_people(params={"limit": 1})
    if 'people' not in people_response or not people_response['people']:
        pytest.skip("No people available for testing")
    return people_response['people'][0]['id']

@pytest.fixture
def test_note_id(notes_api, test_person_id):
    """Create a test note to add reactions to."""
    # Create a note
    response = notes_api.create_note(
        person_id=test_person_id,
        subject="Test Note for Reactions",
        body="This is a test note for adding reactions."
    )
    note_id = response['id']
    
    yield note_id
    
    # Clean up the note after test
    try:
        notes_api.delete_note(note_id)
    except Exception as e:
        print(f"Error cleaning up test note: {e}")

def test_create_and_retrieve_note_with_reaction(reactions_api, notes_api, test_note_id):
    """Test creating a reaction on a note and then retrieving the note with reactions."""
    # Add a reaction to the note
    emoji = "👍"
    ref_type = "note"
    
    # Create a reaction
    response = reactions_api.create_reaction(ref_type, test_note_id, emoji)
    
    # Verify the response - this might be an empty array or contain minimal data
    print(f"Create reaction response: {response}")
    
    # Retrieve the note with reactions included
    note_with_reactions = notes_api.retrieve_note(test_note_id, params={"includeReactions": True})
    
    # Verify the note has the reaction
    assert 'reactions' in note_with_reactions
    
    # Find our reaction
    found_reaction = False
    reaction_id = None
    for reaction in note_with_reactions['reactions']:
        if reaction.get('body') == emoji:
            found_reaction = True
            if 'id' in reaction:
                reaction_id = reaction['id']
            break
    
    assert found_reaction, "Reaction was not found on the note"
    
    # If we found a reaction ID, test the retrieve_reaction endpoint
    if reaction_id:
        retrieved_reaction = reactions_api.retrieve_reaction(reaction_id)
        print(f"Retrieved reaction: {retrieved_reaction}")
        assert retrieved_reaction.get('body') == emoji
    
    # Test deleting the reaction
    delete_response = reactions_api.delete_reaction(ref_type, test_note_id, emoji)
    print(f"Delete reaction response: {delete_response}")
    
    # Verify the reaction was deleted by retrieving the note again
    note_after_delete = notes_api.retrieve_note(test_note_id, params={"includeReactions": True})
    
    # Verify the reaction is gone or the reactions list is empty
    if 'reactions' in note_after_delete:
        for reaction in note_after_delete['reactions']:
            assert reaction.get('body') != emoji, "Reaction was not deleted" 