"""
Test the Email Templates API.
"""

import pytest
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient
from follow_up_boss_api.email_templates import EmailTemplates
import os
import requests
from follow_up_boss_api.client import FollowUpBossApiException

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )

@pytest.fixture
def email_templates_api(client):
    """Create an EmailTemplates instance for testing."""
    return EmailTemplates(client)

def test_list_email_templates(email_templates_api):
    """Test listing email templates."""
    # List email templates with minimal parameters
    params = {"limit": 5}  # Limit to 5 to keep response size manageable
    try:
        response = email_templates_api.list_email_templates(**params)
        
        # Debug print
        print("Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert '_metadata' in response
        
        # The API might return 'templates' or a similar key
        if 'templates' in response:
            assert isinstance(response['templates'], list)
        elif 'emailTemplates' in response:
            assert isinstance(response['emailTemplates'], list)
        else:
            # If neither key exists, check metadata for expected collection name
            assert 'collection' in response['_metadata']
            expected_collections = ['templates', 'emailTemplates']
            assert response['_metadata']['collection'] in expected_collections
    except requests.exceptions.HTTPError as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.response.status_code == 403:
            pytest.skip(f"API key doesn't have access to Email Templates: {str(e)}")
        else:
            raise

def create_test_email_template(email_templates_api):
    """Create a test email template and return its ID and details."""
    # Generate a unique name for the template to avoid conflicts
    unique_suffix = uuid.uuid4().hex[:8]
    name = f"Test Template {unique_suffix}"
    subject = f"Test Subject {unique_suffix}"
    body = f"""
    <html>
    <body>
        <h1>Test Email Template {unique_suffix}</h1>
        <p>This is a test template body created for API testing.</p>
        <p>It includes {{{{firstName}}}} as a merge field.</p>
    </body>
    </html>
    """
    
    try:
        response = email_templates_api.create_email_template(
            name=name,
            subject=subject,
            body=body
        )
        
        # Debug print
        print(f"Create Template Response:", response)
        
        if isinstance(response, dict) and 'id' in response:
            template_id = response['id']
            return template_id, {
                'name': name,
                'subject': subject,
                'body': body
            }
        else:
            pytest.skip(f"Failed to create test email template, unexpected response: {response}")
            return None, None
    except requests.exceptions.HTTPError as e:
        # If we get a 403, it might mean the API key doesn't have access to this endpoint
        if e.response.status_code == 403:
            pytest.skip(f"API key doesn't have access to create Email Templates: {str(e)}")
        else:
            raise

def test_create_email_template(email_templates_api):
    """Test creating an email template."""
    # Generate a unique name for the template
    unique_suffix = uuid.uuid4().hex[:8]
    name = f"Test Template {unique_suffix}"
    subject = f"Test Subject {unique_suffix}"
    body = f"""
    <html>
    <body>
        <h1>Test Email Template {unique_suffix}</h1>
        <p>This is a test template body created for API testing.</p>
        <p>It includes {{{{firstName}}}} as a merge field.</p>
    </body>
    </html>
    """
    
    try:
        response = email_templates_api.create_email_template(
            name=name,
            subject=subject,
            body=body
        )
        
        # Debug print
        print(f"Create Email Template Response:", response)
        
        # Basic assertions about the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert 'name' in response
        assert 'subject' in response
        assert 'body' in response
        
        # Verify the template details match what we sent
        assert response['name'] == name
        assert response['subject'] == subject
        
        # Return the template ID for use in subsequent tests
        return response['id']
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to create templates: {str(e)}")
        else:
            raise

def test_retrieve_email_template(email_templates_api):
    """Test retrieving an email template."""
    # First, attempt to create a template or get an existing one
    try:
        template_id, template_data = create_test_email_template(email_templates_api)
        if not template_id:
            # If we couldn't create a test template, try to get the first one from the list
            list_response = email_templates_api.list_email_templates(limit=1)
            if (
                isinstance(list_response, dict) 
                and ('templates' in list_response or 'emailTemplates' in list_response)
            ):
                templates_list = list_response.get('templates', list_response.get('emailTemplates', []))
                if templates_list:
                    template_id = templates_list[0]['id']
                else:
                    pytest.skip("No email templates available to test retrieval")
            else:
                pytest.skip("Could not list email templates to find one to retrieve")
        
        # Now retrieve the template
        response = email_templates_api.retrieve_email_template(template_id)
        
        # Debug print
        print(f"Retrieve Template {template_id} Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert response['id'] == template_id
        
        # Additional assertions if we created the template and know what to expect
        if template_data:
            assert 'name' in response
            assert 'subject' in response
            assert response['name'] == template_data['name']
            assert response['subject'] == template_data['subject']
    
    except requests.exceptions.HTTPError as e:
        # If we get a permission error, skip the test
        if e.response.status_code in [401, 403]:
            pytest.skip(f"API key doesn't have permission to retrieve templates: {str(e)}")
        else:
            raise

def test_update_email_template(email_templates_api):
    """Test updating an email template."""
    # First, create a test template to update
    try:
        template_id, template_data = create_test_email_template(email_templates_api)
        
        if not template_id:
            pytest.skip("Could not create a test email template to update")
        
        # Generate new data for the update
        updated_name = f"Updated Template {uuid.uuid4().hex[:8]}"
        updated_subject = f"Updated Subject {uuid.uuid4().hex[:8]}"
        updated_body = f"""
        <html>
        <body>
            <h1>Updated Email Template</h1>
            <p>This is an updated test template body.</p>
            <p>It has been modified at {uuid.uuid4().hex[:8]}.</p>
        </body>
        </html>
        """
        
        update_data = {
            "name": updated_name,
            "subject": updated_subject,
            "body": updated_body  # Include body to avoid "Template body cannot be blank" error
        }
        
        # Update the template
        response = email_templates_api.update_email_template(template_id, update_data)
        
        # Debug print
        print(f"Update Template {template_id} Response:", response)
        
        # Check basic structure of the response
        assert isinstance(response, dict)
        assert 'id' in response
        assert response['id'] == template_id
        
        # Verify the updated data
        assert 'name' in response
        assert 'subject' in response
        assert 'body' in response
        assert response['name'] == updated_name
        assert response['subject'] == updated_subject
    
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

def test_merge_email_template(email_templates_api):
    """Test merging fields into an email template."""
    # First, create a template to use for merging
    try:
        template_id, template_data = create_test_email_template(email_templates_api)
        
        if not template_id:
            pytest.skip("Could not create a test email template for merging")
        
        # Define merge fields
        merge_fields = {
            "firstName": "Test",
            "lastName": "User"
        }
        
        # Test merge with an existing template ID
        response = email_templates_api.merge_email_template(
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
        if 'subject' in response:
            assert template_data['subject'] in response['subject']  # Original subject should be there
    
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

def test_delete_email_template(email_templates_api):
    """Test deleting an email template."""
    # First, create a test template to delete
    try:
        template_id, _ = create_test_email_template(email_templates_api)
        
        if not template_id:
            pytest.skip("Could not create a test email template to delete")
        
        # Delete the template
        response = email_templates_api.delete_email_template(template_id)
        
        # Debug print
        print(f"Delete Template {template_id} Response:", response)
        
        # For successful deletion, the response might be empty or a success message
        
        # Verify deletion by attempting to retrieve the template
        with pytest.raises(FollowUpBossApiException) as excinfo:
            email_templates_api.retrieve_email_template(template_id)
            
        # Check that it was properly deleted (404 Not Found)
        assert excinfo.value.status_code == 404
            
    except FollowUpBossApiException as e:
        # If we get an unexpected exception, print it and fail
        print(f"Unexpected error: {e}")
        raise

def test_retrieve_nonexistent_email_template(email_templates_api):
    """Test retrieving an email template that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999
    
    # Attempt to retrieve the template, expecting a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        email_templates_api.retrieve_email_template(nonexistent_id)
    
    # Check that it's a 404 error
    assert excinfo.value.status_code == 404
    print(f"Received expected 404 error: {excinfo.value}") 