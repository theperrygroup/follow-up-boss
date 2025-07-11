"""
Test the Teams API.
"""

import os
import uuid

import pytest

from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.teams import Teams


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def teams_api(client):
    """Create a Teams instance for testing."""
    return Teams(client)


def test_list_teams(teams_api):
    """Test listing teams."""
    response = teams_api.list_teams()

    # Debug info
    print(f"List teams response: {response}")

    # Verify structure
    assert isinstance(response, dict)
    assert "_metadata" in response

    # Check that we have the teams list (look for expected key)
    expected_keys = ["teams", "data", "payload", "items"]
    has_data_key = False
    for key in expected_keys:
        if key in response:
            assert isinstance(response[key], list)
            has_data_key = True
            break

    if not has_data_key:
        # If no explicit data key, check if _metadata indicates what the collection is
        assert "collection" in response["_metadata"]
        assert response["_metadata"]["collection"] in ["teams", "team"]


def test_retrieve_team(teams_api):
    """Test retrieving a team."""
    # First, list teams to find one
    response = teams_api.list_teams()

    # Find a key with teams data
    teams_key = None
    for key in response:
        if key in ["teams", "data", "payload", "items"] and isinstance(
            response[key], list
        ):
            teams_key = key
            break

    if not teams_key or not response[teams_key]:
        pytest.skip("No teams available for testing")

    # Use the first team ID for testing
    team_id = response[teams_key][0]["id"]

    # Retrieve the team
    retrieve_response = teams_api.retrieve_team(team_id)

    # Debug info
    print(f"Retrieve team {team_id} response: {retrieve_response}")

    # Verify structure
    assert isinstance(retrieve_response, dict)
    assert "id" in retrieve_response
    assert retrieve_response["id"] == team_id


def test_create_update_delete_team():
    """
    Test creating, updating, and deleting a team.

    This test is skipped because team creation/updates/deletion may require
    admin permissions and could affect production data.
    """
    pytest.skip(
        "Team creation/update/deletion tests are skipped to avoid disrupting production data. "
        "These operations typically require admin permissions."
    )

    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    teams_api = Teams(client)

    # Generate unique test data
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"Test Team {unique_id}"

    try:
        # Create team
        create_response = teams_api.create_team(name=test_name)

        print(f"Create team response: {create_response}")
        assert "id" in create_response
        team_id = create_response["id"]

        # Update team
        updated_name = f"Updated Team {unique_id}"
        update_response = teams_api.update_team(
            team_id=team_id, update_data={"name": updated_name}
        )

        print(f"Update team response: {update_response}")
        assert update_response["name"] == updated_name

        # Delete team
        delete_response = teams_api.delete_team(team_id)

        print(f"Delete team response: {delete_response}")

        # Verify deletion
        with pytest.raises(FollowUpBossApiException) as excinfo:
            teams_api.retrieve_team(team_id)

        assert excinfo.value.status_code in [
            404,
            410,
        ], f"Expected 404 or 410, got {excinfo.value.status_code}"

    except FollowUpBossApiException as e:
        if "Permission denied" in str(e) or "access" in str(e).lower():
            pytest.skip(f"API permission denied: {e}")
        else:
            raise
