"""
Test the Custom Fields API.
"""

import pytest
import uuid
from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.custom_fields import CustomFields
import os
import requests
from follow_up_boss.client import FollowUpBossApiException
import json

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )

@pytest.fixture
def custom_fields_api(client):
    """Create a CustomFields instance for testing."""
    return CustomFields(client)

def test_list_custom_fields(custom_fields_api):
    """Test listing custom fields."""
    try:
        response = custom_fields_api.list_custom_fields()
        
        # Detailed debug prints
        print("\n\n============== RESPONSE START ==============")
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys())}")
        
        # Print full response
        print(json.dumps(response, indent=2))
        print("============== RESPONSE END ==============\n")
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        
        # Check if the response contains custom fields with correct collection name
        assert '_metadata' in response
        assert 'customfields' in response
        
        # Check metadata
        assert 'collection' in response['_metadata']
        assert response['_metadata']['collection'] == 'customfields'
        
        # Verify the list of fields exists
        assert isinstance(response['customfields'], list)
            
    except requests.exceptions.HTTPError as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.response.status_code == 403:
            pytest.skip(f"API key doesn't have access to Custom Fields: {str(e)}")
        else:
            raise

def test_retrieve_custom_field(custom_fields_api):
    """Test retrieving a custom field."""
    try:
        # Get the first custom field from the list
        list_response = custom_fields_api.list_custom_fields()
        field_list = list_response['customfields']
        
        if not field_list or len(field_list) == 0:
            pytest.skip("No custom fields available to test retrieval")
        
        # Use the first field for testing
        field_id = field_list[0]['id']
        field_data = field_list[0]
        
        # Now retrieve the field
        response = custom_fields_api.retrieve_custom_field(field_id)
        
        # Debug print
        print(f"Retrieve Custom Field {field_id} Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert response['id'] == field_id
        
        # Additional assertions based on the field we know exists
        assert 'name' in response
        assert response['name'] == field_data['name']
        
        # Type should be in 'type'
        assert 'type' in response
        assert response['type'].lower() == field_data['type'].lower()
    
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to retrieve custom fields: {str(e)}")
        else:
            print(f"HTTP error retrieving custom field: {str(e)}")
            print(f"Response content: {e.response.content if hasattr(e, 'response') else 'No response content'}")
            raise

def test_update_custom_field(custom_fields_api):
    """Test updating a custom field."""
    try:
        # Get a custom field to update
        list_response = custom_fields_api.list_custom_fields()
        field_list = list_response['customfields']
        
        if not field_list or len(field_list) == 0:
            pytest.skip("No custom fields available to test update")
        
        # Use the first field for testing
        field_id = field_list[0]['id']
        original_label = field_list[0]['label']
        
        # Generate a unique label for testing
        unique_suffix = uuid.uuid4().hex[:8]
        new_label = f"Updated Label {unique_suffix}"
        
        try:
            # Update the field's label
            update_data = {"label": new_label}
            response = custom_fields_api.update_custom_field(field_id, update_data)
            
            # Debug print
            print(f"Update Custom Field {field_id} Response:", response)
            
            # Check basic structure of the response
            assert isinstance(response, dict)
            assert 'id' in response
            assert response['id'] == field_id
            
            # Verify the updated data
            assert 'label' in response
            assert response['label'] == new_label
            
            # Restore the original label
            custom_fields_api.update_custom_field(field_id, {"label": original_label})
            
        except Exception as e:
            # Attempt to restore the original label if the test fails
            try:
                custom_fields_api.update_custom_field(field_id, {"label": original_label})
            except:
                print(f"Warning: Could not restore original label '{original_label}' for field {field_id}")
            raise e
    
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to update custom fields: {str(e)}")
        else:
            print(f"HTTP error updating custom field: {str(e)}")
            print(f"Response content: {e.response.content if hasattr(e, 'response') else 'No response content'}")
            raise

def test_retrieve_nonexistent_custom_field(custom_fields_api):
    """Test retrieving a custom field that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999
    
    # Attempt to retrieve the field, expecting a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        custom_fields_api.retrieve_custom_field(nonexistent_id)
    
    # Check that it's a 404 or 400 error
    # Some APIs return 400 Bad Request for non-existent resources
    assert excinfo.value.status_code in [404, 400] 