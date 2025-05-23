"""
Test the Webhooks API.
"""

import pytest
import os
import uuid
from follow_up_boss_api.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss_api.webhooks import Webhooks


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )


@pytest.fixture
def webhooks_api(client):
    """Create a Webhooks instance for testing."""
    return Webhooks(client)


def test_list_webhooks(webhooks_api):
    """Test listing webhooks."""
    response = webhooks_api.list_webhooks()
    
    # Debug info
    print(f"List webhooks response: {response}")
    
    # Verify structure
    assert isinstance(response, dict)
    assert "_metadata" in response
    
    # Check that we have the webhooks list (look for expected key)
    expected_keys = ['webhooks', 'data', 'payload', 'items']
    has_data_key = False
    for key in expected_keys:
        if key in response:
            assert isinstance(response[key], list)
            has_data_key = True
            break
    
    if not has_data_key:
        # If no explicit data key, check if _metadata indicates what the collection is
        assert "collection" in response["_metadata"]
        assert response["_metadata"]["collection"] in ["webhooks", "webhook"]


def test_webhook_operations():
    """
    Test full webhook lifecycle (create, retrieve, update, delete).
    
    This test is marked as skipped because webhook creation requires 
    a publicly accessible URL for the webhook endpoint.
    """
    pytest.skip(
        "Webhook creation requires a publicly accessible URL and is disruptive. "
        "To test manually, set up a webhook receiver and update the test URL."
    )
    
    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )
    webhooks_api = Webhooks(client)
    
    # Use a test webhook URL (you would need a real endpoint for actual testing)
    # In a real environment, you might use a service like RequestBin or Webhook.site
    test_url = "https://webhook.site/your-unique-id"
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"Test Webhook {unique_id}"
    
    try:
        # Create webhook
        created = webhooks_api.create_webhook(
            url=test_url,
            event_types=["PERSON_CREATED", "NOTE_CREATED"],
            name=test_name
        )
        
        print(f"Created webhook: {created}")
        assert "id" in created
        webhook_id = created["id"]
        
        # Retrieve webhook
        retrieved = webhooks_api.retrieve_webhook(webhook_id)
        print(f"Retrieved webhook: {retrieved}")
        assert retrieved["name"] == test_name
        assert retrieved["url"] == test_url
        
        # Update webhook
        updated_name = f"Updated Webhook {unique_id}"
        updated = webhooks_api.update_webhook(
            webhook_id=webhook_id,
            name=updated_name
        )
        print(f"Updated webhook: {updated}")
        assert updated["name"] == updated_name
        
        # Delete webhook
        deleted = webhooks_api.delete_webhook(webhook_id)
        print(f"Deleted webhook response: {deleted}")
        
        # Verify deletion
        with pytest.raises(FollowUpBossApiException) as excinfo:
            webhooks_api.retrieve_webhook(webhook_id)
        
        assert excinfo.value.status_code in [404, 410], f"Expected 404 or 410, got {excinfo.value.status_code}"
        
    except FollowUpBossApiException as e:
        if "Permission denied" in str(e) or "access" in str(e).lower():
            pytest.skip(f"API permission denied: {e}")
        else:
            raise 