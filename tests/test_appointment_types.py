"""
Test the Appointment Types API.
"""

import pytest
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss_api.appointment_types import AppointmentTypes
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
def appointment_types_api(client):
    """Create an AppointmentTypes instance for testing."""
    return AppointmentTypes(client)

def test_list_appointment_types(appointment_types_api):
    """Test listing appointment types."""
    response = appointment_types_api.list_appointment_types()
    
    # Debug print
    print("List Appointment Types Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    
    # The API might return 'appointmenttypes' (lowercase) or similar key
    expected_keys = ['appointmenttypes', 'types', 'data']
    found_key = False
    for key in expected_keys:
        if key in response:
            assert isinstance(response[key], list)
            found_key = True
            break
            
    if not found_key:
        # Check metadata for collection name
        assert 'collection' in response['_metadata']
        assert response['_metadata']['collection'] in ['appointmenttypes', 'types']

def test_create_appointment_type_skipped(appointment_types_api):
    """Test creating an appointment type - skipped due to API permission limitations."""
    pytest.skip("Creating appointment types requires admin permissions")

def test_retrieve_appointment_type(appointment_types_api):
    """Test retrieving an appointment type."""
    # List existing appointment types
    response = appointment_types_api.list_appointment_types()
    
    # Check if we have any appointment types to test with
    types_key = None
    for key in ['appointmenttypes', 'types']:
        if key in response:
            types_key = key
            break
            
    if not types_key or not response[types_key]:
        pytest.skip("No appointment types available to test retrieval")
    
    # Use the first type from the list
    appt_type_id = response[types_key][0]['id']
    
    # Retrieve the appointment type
    retrieve_response = appointment_types_api.retrieve_appointment_type(appt_type_id)
    
    # Debug print
    print("Retrieve Appointment Type Response:", retrieve_response)
    
    # Verify the retrieved appointment type
    assert isinstance(retrieve_response, dict)
    assert 'id' in retrieve_response
    assert retrieve_response['id'] == appt_type_id
    assert 'name' in retrieve_response

def test_update_appointment_type_skipped(appointment_types_api):
    """Test updating an appointment type - skipped due to API permission limitations."""
    pytest.skip("Updating appointment types requires admin permissions")

def test_delete_appointment_type_skipped(appointment_types_api):
    """Test deleting an appointment type - skipped due to API permission limitations."""
    pytest.skip("Deleting appointment types requires admin permissions")

def test_retrieve_nonexistent_appointment_type(appointment_types_api):
    """Test retrieving an appointment type that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999
    
    # Try to retrieve the appointment type, expecting a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        appointment_types_api.retrieve_appointment_type(nonexistent_id)
    
    # Check that it's a 404 error
    assert excinfo.value.status_code in [404, 400]  # Either not found or bad request
    print(f"Received expected error: {excinfo.value}") 