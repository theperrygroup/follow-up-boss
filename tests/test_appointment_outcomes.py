"""
Test the Appointment Outcomes API.
"""

import pytest
import uuid
from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.appointment_outcomes import AppointmentOutcomes
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
def appointment_outcomes_api(client):
    """Create an AppointmentOutcomes instance for testing."""
    return AppointmentOutcomes(client)

def test_list_appointment_outcomes(appointment_outcomes_api):
    """Test listing appointment outcomes."""
    response = appointment_outcomes_api.list_appointment_outcomes()
    
    # Debug print
    print("List Appointment Outcomes Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    
    # The API might return 'appointmentoutcomes' (lowercase) or similar key
    expected_keys = ['appointmentoutcomes', 'outcomes', 'data']
    found_key = False
    for key in expected_keys:
        if key in response:
            assert isinstance(response[key], list)
            found_key = True
            break
            
    if not found_key:
        # Check metadata for collection name
        assert 'collection' in response['_metadata']
        assert response['_metadata']['collection'] in ['appointmentoutcomes', 'outcomes']

def test_create_appointment_outcome_skipped(appointment_outcomes_api):
    """Test creating an appointment outcome - skipped due to API permission limitations."""
    pytest.skip("Creating appointment outcomes requires admin permissions")

def test_retrieve_appointment_outcome(appointment_outcomes_api):
    """Test retrieving an appointment outcome."""
    # List existing appointment outcomes
    response = appointment_outcomes_api.list_appointment_outcomes()
    
    # Check if we have any appointment outcomes to test with
    outcomes_key = 'appointmentoutcomes'
    if outcomes_key not in response or not response[outcomes_key]:
        pytest.skip("No appointment outcomes available to test retrieval")
    
    # Use the first outcome from the list
    outcome_id = response[outcomes_key][0]['id']
    
    # Retrieve the outcome
    retrieve_response = appointment_outcomes_api.retrieve_appointment_outcome(outcome_id)
    
    # Debug print
    print("Retrieve Appointment Outcome Response:", retrieve_response)
    
    # Verify the retrieved outcome
    assert isinstance(retrieve_response, dict)
    assert 'id' in retrieve_response
    assert retrieve_response['id'] == outcome_id
    assert 'name' in retrieve_response

def test_update_appointment_outcome_skipped(appointment_outcomes_api):
    """Test updating an appointment outcome - skipped due to API permission limitations."""
    pytest.skip("Updating appointment outcomes requires admin permissions")

def test_delete_appointment_outcome_skipped(appointment_outcomes_api):
    """Test deleting an appointment outcome - skipped due to API permission limitations."""
    pytest.skip("Deleting appointment outcomes requires assignOutcomeId and admin permissions")

def test_retrieve_nonexistent_appointment_outcome(appointment_outcomes_api):
    """Test retrieving an appointment outcome that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999
    
    # Try to retrieve the outcome, expecting a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        appointment_outcomes_api.retrieve_appointment_outcome(nonexistent_id)
    
    # Check that it's a 404 error
    assert excinfo.value.status_code in [404, 400]  # Either not found or bad request
    print(f"Received expected error: {excinfo.value}") 