"""
Test the Team Inboxes API.
"""

import os

import pytest

from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.team_inboxes import TeamInboxes


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def team_inboxes_api(client):
    """Create a TeamInboxes instance for testing."""
    return TeamInboxes(client)


def test_list_team_inboxes(team_inboxes_api):
    """Test listing team inboxes."""
    response = team_inboxes_api.list_team_inboxes()

    # Debug print
    print("Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "_metadata" in response
    assert "teamInboxes" in response  # Note the capitalization

    # Check metadata
    assert "collection" in response["_metadata"]
    assert response["_metadata"]["collection"] == "teamInboxes"

    # Check team inboxes data (might be empty in test account)
    assert isinstance(response["teamInboxes"], list)
