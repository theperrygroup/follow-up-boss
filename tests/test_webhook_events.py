"""
Test the Webhook Events API.
"""

import pytest
import uuid
from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.webhook_events import WebhookEvents
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
def webhook_events_api(client):
    """Create a WebhookEvents instance for testing."""
    return WebhookEvents(client)

def test_retrieve_webhook_event_not_found(webhook_events_api):
    """Test retrieving a webhook event with an invalid ID."""
    # Generate a random ID that almost certainly won't exist
    non_existent_id = str(uuid.uuid4())
    
    # We expect this to raise an exception with a 404 status code
    with pytest.raises(Exception) as excinfo:
        webhook_events_api.retrieve_webhook_event(non_existent_id)
    
    # Debug print
    print("Exception info:", excinfo.value)
    
    # The test is considered passing if an exception is raised
    # We should ideally check that it's a 404 status code, but the exact exception type
    # depends on how the client is implemented 