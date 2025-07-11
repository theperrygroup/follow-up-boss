"""
Test the Inbox Apps API.
"""

import os
import uuid

import pytest

from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.inbox_apps import InboxApps


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def inbox_apps_api(client):
    """Create an InboxApps instance for testing."""
    return InboxApps(client)


def test_inbox_apps_operations():
    """
    Test inbox apps operations.

    This test is skipped because inbox app operations require specific
    app configurations and permissions.
    """
    pytest.skip(
        "Inbox app operations require specific app configurations and permissions. "
        "These operations are marked as implemented but require manual testing."
    )

    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    inbox_apps_api = InboxApps(client)

    # Generate unique test data
    unique_id = str(uuid.uuid4())[:8]
    app_name = f"Test App {unique_id}"
    app_id = f"test_app_{unique_id}"
    username = f"test_user_{unique_id}"

    try:
        # Install app
        install_response = inbox_apps_api.install_inbox_app(
            app_name=app_name, app_id=app_id, username=username
        )

        print(f"Install app response: {install_response}")

        # Create a conversation
        conversation_id = f"conv_{unique_id}"

        # Add message
        message_response = inbox_apps_api.add_message(
            conversation_id=conversation_id, body="Test message", sender=username
        )

        print(f"Add message response: {message_response}")

        # Get message ID from response
        message_id = message_response["id"]

        # Update message
        update_message_response = inbox_apps_api.update_message(
            message_id=message_id, status="read"
        )

        print(f"Update message response: {update_message_response}")

        # Add note
        note_response = inbox_apps_api.add_note(
            conversation_id=conversation_id, body="Test note", created_by=username
        )

        print(f"Add note response: {note_response}")

        # Update conversation
        update_conversation_response = inbox_apps_api.update_conversation(
            conversation_id=conversation_id, status="closed"
        )

        print(f"Update conversation response: {update_conversation_response}")

        # Get participants
        participants_response = inbox_apps_api.get_participants(
            conversation_id=conversation_id
        )

        print(f"Get participants response: {participants_response}")

        # Add participant
        add_participant_response = inbox_apps_api.add_participant(
            conversation_id=conversation_id,
            participant_id="1",  # Example user ID
            participant_type="user",
        )

        print(f"Add participant response: {add_participant_response}")

        # Remove participant
        remove_participant_response = inbox_apps_api.remove_participant(
            conversation_id=conversation_id, participant_id="1", participant_type="user"
        )

        print(f"Remove participant response: {remove_participant_response}")

        # Deactivate app
        deactivate_response = inbox_apps_api.deactivate(app_id=app_id)

        print(f"Deactivate app response: {deactivate_response}")

    except FollowUpBossApiException as e:
        if "Permission denied" in str(e) or "access" in str(e).lower():
            pytest.skip(f"API permission denied: {e}")
        else:
            raise
