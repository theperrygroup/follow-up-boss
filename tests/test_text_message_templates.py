"""
Test the Text Message Templates API.
"""

import pytest
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.text_message_templates import TextMessageTemplates
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
def text_message_templates_api(client):
    """Create a TextMessageTemplates instance for testing."""
    return TextMessageTemplates(client)

def test_list_text_message_templates(text_message_templates_api):
    """Test listing text message templates."""
    # List text message templates with minimal parameters
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    try:
        response = text_message_templates_api.list_text_message_templates(**params)
        
        # Debug print
        print("Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert '_metadata' in response
        
        # The API might return 'templates' or a similar key
        if 'textMessageTemplates' in response:
            assert isinstance(response['textMessageTemplates'], list)
        elif 'templates' in response:
            assert isinstance(response['templates'], list)
        else:
                            # If neither key exists, check metadata for expected collection name
                assert 'collection' in response['_metadata']
                expected_collections = ['textMessageTemplates', 'templates', 'textmessagetemplates']
                assert response['_metadata']['collection'] in expected_collections
    except requests.exceptions.HTTPError as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.response.status_code == 403:
            pytest.skip(f"API key doesn't have access to Text Message Templates: {str(e)}")
        else:
            raise

def create_test_text_message_template(text_message_templates_api):
    """Create a test text message template and return its ID and details."""
    # Generate a unique name for the template to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    name = f"Test SMS Template {unique_suffix}"
    body = f"This is a test text message template created for API testing. It includes {{firstName}} as a merge field. ID: {unique_suffix}"
    
    try:
        response = text_message_templates_api.create_text_message_template(
            name=name,
            body=body
        )
        
        # Debug print
        print(f"Create Template Response:", response)
        
        if isinstance(response, dict) and 'id' in response:
            template_id = response['id']
            return template_id, {
                'name': name,
                'body': body
            }
        else:
            pytest.skip(f"Failed to create test text message template, unexpected response: {response}")
            return None, None
    except requests.exceptions.HTTPError as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.response.status_code == 403:
            pytest.skip(f"API key doesn't have access to create Text Message Templates: {str(e)}")
        else:
            raise

def test_create_text_message_template(text_message_templates_api):
    """Test creating a text message template."""
    # Generate a unique name for the template
    unique_suffix = uuid.uuid4().hex[:8]
    name = f"Test SMS Template {unique_suffix}"
    body = f"This is a test text message template created for API testing. It includes {{firstName}} as a merge field. ID: {unique_suffix}"
    
    try:
        response = text_message_templates_api.create_text_message_template(
            name=name,
            body=body
        )
        
        # Debug print
        print(f"Create Text Message Template Response:", response)
        
        # Basic assertions about the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert 'name' in response
        
        # Check for either 'message' or 'body' field
        assert 'message' in response or 'body' in response
        
        # Verify the template details match what we sent
        assert response['name'] == name
        
        message_field = 'message' if 'message' in response else 'body'
        assert body in response[message_field]
        
        # Return the template ID for potential future use
        return response['id']
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to create templates: {str(e)}")
        else:
            raise

def test_retrieve_text_message_template(text_message_templates_api):
    """Test retrieving a text message template."""
    # First, attempt to create a template or get an existing one
    try:
        template_id, template_data = create_test_text_message_template(text_message_templates_api)
        if not template_id:
            # If we couldn't create a test template, try to get the first one from the list
            list_response = text_message_templates_api.list_text_message_templates(limit=1)
            if (
                isinstance(list_response, dict) 
                and ('textMessageTemplates' in list_response or 'templates' in list_response)
            ):
                templates_list = list_response.get('textMessageTemplates', list_response.get('templates', []))
                if templates_list:
                    template_id = templates_list[0]['id']
                else:
                    pytest.skip("No text message templates available to test retrieval")
            else:
                pytest.skip("Could not list text message templates to find one to retrieve")
        
        # Now retrieve the template
        response = text_message_templates_api.retrieve_text_message_template(template_id)
        
        # Debug print
        print(f"Retrieve Template {template_id} Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert response['id'] == template_id
        
        # Additional assertions if we created the template and know what to expect
        if template_data:
            assert 'name' in response
            assert response['name'] == template_data['name']
            
            # Check for either 'message' or 'body' field
            message_field = 'message' if 'message' in response else 'body'
            assert message_field in response
            # The template body might be formatted differently when retrieved
            assert template_data['body'] in response[message_field]
    
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to retrieve templates: {str(e)}")
        else:
            raise

def test_update_text_message_template(text_message_templates_api):
    """Test updating a text message template."""
    # First, create a test template to update
    try:
        template_id, template_data = create_test_text_message_template(text_message_templates_api)
        
        if not template_id:
            pytest.skip("Could not create a test text message template to update")
        
        # Generate new data for the update
        updated_name = f"Updated SMS Template {uuid.uuid4().hex[:8]}"
        updated_body = f"This is an updated text message template. Time of update: {uuid.uuid4().hex[:8]}"
        
        # Retrieve the template first to see what field name is used for the message body
        original = text_message_templates_api.retrieve_text_message_template(template_id)
        message_field = 'message' if 'message' in original else 'body'
        
        update_data = {
            "name": updated_name,
            message_field: updated_body
        }
        
        # Update the template
        response = text_message_templates_api.update_text_message_template(template_id, update_data)
        
        # Debug print
        print(f"Update Template {template_id} Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert response['id'] == template_id
        
        # Verify the updated data
        assert 'name' in response
        assert message_field in response
        assert response['name'] == updated_name
        assert updated_body in response[message_field]
    
    except requests.exceptions.HTTPError as e:
        # Get the response content for more detailed error information
        print(f"HTTP error occurred: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'content'):
            print(f"Response content: {e.response.content}")
        
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to update templates: {str(e)}")
        else:
            raise

def test_merge_text_message_template(text_message_templates_api):
    """Test merging fields into a text message template."""
    # First, create a template to use for merging
    try:
        template_id, template_data = create_test_text_message_template(text_message_templates_api)
        
        if not template_id:
            pytest.skip("Could not create a test text message template for merging")
        
        # Define merge fields
        merge_fields = {
            "firstName": "Test",
            "lastName": "User"
        }
        
        # Test merge with an existing template ID
        response = text_message_templates_api.merge_text_message_template(
            body="",  # We'll use the template's body
            merge_fields=merge_fields,
            template_id=template_id  # Using the template we created
        )
        
        # Debug print
        print(f"Merge Template Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        
        # Verify that merge fields were processed
        if 'body' in response:
            assert "Test" in response['body']  # The firstName field should be replaced
    
    except requests.exceptions.HTTPError as e:
        # Get the response content for more detailed error information
        print(f"HTTP error occurred: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'content'):
            print(f"Response content: {e.response.content}")
        
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to merge templates: {str(e)}")
        else:
            raise

def test_delete_text_message_template(text_message_templates_api):
    """Test deleting a text message template."""
    # First, create a test template to delete
    try:
        template_id, _ = create_test_text_message_template(text_message_templates_api)
        
        if not template_id:
            pytest.skip("Could not create a test text message template to delete")
        
        # Delete the template
        response = text_message_templates_api.delete_text_message_template(template_id)
        
        # Debug print
        print(f"Delete Template {template_id} Response:", response)
        
        # For successful deletion, the response might be empty or a success message
        
        # Verify deletion by attempting to retrieve the template
        try:
            text_message_templates_api.retrieve_text_message_template(template_id)
            # If we get here, the template wasn't deleted
            assert False, f"Template {template_id} was not deleted properly"
        except requests.exceptions.HTTPError as e:
            # Expected: template should not be found
            assert e.response.status_code == 404
            print(f"Expected error when retrieving deleted template: {e}")
    
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to delete templates: {str(e)}")
        else:
            raise

def test_retrieve_nonexistent_text_message_template(text_message_templates_api):
    """Test retrieving a text message template that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999
    
    # Attempt to retrieve the template, expecting a 404
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        text_message_templates_api.retrieve_text_message_template(nonexistent_id)
    
    # Check that it's a 404 error
    assert excinfo.value.response.status_code == 404
    print(f"Received expected 404 error: {excinfo.value}") 