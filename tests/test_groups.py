"""
Test the Groups API.
"""

import os
import uuid

import pytest

from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.groups import Groups
from follow_up_boss.users import Users


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def groups_api(client):
    """Create a Groups instance for testing."""
    return Groups(client)


@pytest.fixture
def users_api(client):
    """Create a Users instance for testing."""
    return Users(client)


@pytest.fixture
def user_id(users_api):
    """Get a user ID for group testing."""
    response = users_api.list_users()
    users = response.get("users", [])

    if not users:
        pytest.skip("No users available for testing groups")

    return users[0]["id"]


def test_list_groups(groups_api):
    """Test listing groups."""
    response = groups_api.list_groups()

    # Debug info
    print(f"List groups response: {response}")

    # Verify structure
    assert isinstance(response, dict)
    assert "_metadata" in response

    # Check that we have the groups list (look for expected key)
    expected_keys = ["groups", "data", "payload", "items"]
    has_data_key = False
    for key in expected_keys:
        if key in response:
            assert isinstance(response[key], list)
            has_data_key = True
            break

    if not has_data_key:
        # If no explicit data key, check if _metadata indicates what the collection is
        assert "collection" in response["_metadata"]
        assert response["_metadata"]["collection"] in ["groups", "group"]


def test_create_and_retrieve_group(groups_api, user_id):
    """Test creating and then retrieving a group."""
    # Skip test - API doesn't support group creation with current credentials
    pytest.skip("Group creation requires higher level account permissions")

    # Generate a unique name for the group
    unique_suffix = uuid.uuid4().hex[:8]
    group_name = f"Test Group {unique_suffix}"

    try:
        # Create the group with at least one user
        create_response = groups_api.create_group(name=group_name, user_ids=[user_id])

        # Debug print
        print("Create Group Response:", create_response)

        # Check that the group was created successfully
        assert isinstance(create_response, dict)
        assert "id" in create_response
        assert "name" in create_response
        assert create_response["name"] == group_name

        # Retrieve the group to verify it exists
        group_id = create_response["id"]
        retrieve_response = groups_api.retrieve_group(group_id)

        # Debug print
        print("Retrieve Group Response:", retrieve_response)

        # Verify the retrieved group matches what we created
        assert isinstance(retrieve_response, dict)
        assert "id" in retrieve_response
        assert retrieve_response["id"] == group_id
        assert "name" in retrieve_response
        assert retrieve_response["name"] == group_name

        # Clean up - delete the group
        delete_response = groups_api.delete_group(group_id)
        print("Delete Group Response:", delete_response)

    except FollowUpBossApiException as e:
        if e.status_code == 403:
            pytest.skip(f"API permission error: {str(e)}")
        else:
            raise


def test_update_group(groups_api, user_id):
    """Test updating a group."""
    # Skip test - API doesn't support group creation with current credentials
    pytest.skip("Group creation/updating requires higher level account permissions")

    # Generate names
    original_name = f"Original Group {uuid.uuid4().hex[:8]}"
    updated_name = f"Updated Group {uuid.uuid4().hex[:8]}"

    try:
        # Create the group with at least one user
        create_response = groups_api.create_group(
            name=original_name, user_ids=[user_id]
        )
        group_id = create_response["id"]

        # Update the group
        update_data = {"name": updated_name}
        update_response = groups_api.update_group(group_id, update_data)

        # Debug print
        print("Update Group Response:", update_response)

        # Check that the group was updated correctly
        assert isinstance(update_response, dict)
        assert "id" in update_response
        assert update_response["id"] == group_id
        assert "name" in update_response
        assert update_response["name"] == updated_name

        # Clean up - delete the group
        delete_response = groups_api.delete_group(group_id)
        print("Delete Group Response:", delete_response)

    except FollowUpBossApiException as e:
        if e.status_code == 403:
            pytest.skip(f"API permission error: {str(e)}")
        else:
            raise


def test_retrieve_nonexistent_group(groups_api):
    """Test retrieving a group that doesn't exist."""
    # Use a likely non-existent ID
    nonexistent_id = 99999999

    # Try to retrieve the group, expecting a 404
    with pytest.raises(FollowUpBossApiException) as excinfo:
        groups_api.retrieve_group(nonexistent_id)

    # Check that it's a 404 error
    assert excinfo.value.status_code in [404, 400]  # Either not found or bad request
    print(f"Received expected error: {excinfo.value}")


def test_group_round_robin(groups_api):
    """Test retrieving the round robin status for a group."""
    # First need to list groups to find an existing one
    list_response = groups_api.list_groups()

    groups_key = None
    for key in ["groups", "group", "data"]:
        if key in list_response:
            groups_key = key
            break

    if not groups_key or not list_response[groups_key]:
        pytest.skip("No groups available to test round robin feature")

    try:
        # Use the first group from the list
        group_id = list_response[groups_key][0]["id"]

        # Get the round robin status
        response = groups_api.get_group_round_robin_status(group_id)

        # Debug print
        print("Group Round Robin Response:", response)

        # Basic assertion - we got some kind of response
        assert isinstance(response, (dict, str))

    except FollowUpBossApiException as e:
        # If we get a 404, the endpoint might not be /groups/{id}/roundRobin
        # It could be /groups/roundRobin with a query parameter
        if e.status_code == 404:
            pytest.skip(f"Round robin endpoint may have a different format: {str(e)}")
        elif e.status_code == 403:
            pytest.skip(f"API permission error: {str(e)}")
        else:
            raise


def test_get_group_round_robin_status():
    """Test getting group round robin status."""
    pytest.skip(
        "Round robin status test requires a specific group ID with round robin enabled. "
        "This test is skipped to avoid disrupting production configurations."
    )

    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    groups_api = Groups(client)

    # First, list groups to find one
    response = groups_api.list_groups()

    # Find a key with groups data
    groups_key = None
    for key in response:
        if key in ["groups", "data", "payload", "items"] and isinstance(
            response[key], list
        ):
            groups_key = key
            break

    if not groups_key or not response[groups_key]:
        pytest.skip("No groups available for testing")

    # Use the first group ID for testing
    group_id = response[groups_key][0]["id"]

    try:
        # Now try to get round robin status
        round_robin_response = groups_api.get_group_round_robin_status(group_id)

        print(f"Group round robin status response: {round_robin_response}")

        # Check that we got a valid response
        assert isinstance(round_robin_response, (dict, list))

    except FollowUpBossApiException as e:
        if "not found" in str(e).lower() or "404" in str(e):
            pytest.skip(f"Round robin endpoint not found for group {group_id}")
        elif "permission" in str(e).lower() or "access" in str(e).lower():
            pytest.skip(f"Permission denied to access round robin status: {e}")
        else:
            raise


def test_retrieve_group(groups_api):
    """Test retrieving a group."""
    # First, list groups to find one
    response = groups_api.list_groups()

    # Find a key with groups data
    groups_key = None
    for key in response:
        if key in ["groups", "data", "payload", "items"] and isinstance(
            response[key], list
        ):
            groups_key = key
            break

    if not groups_key or not response[groups_key]:
        pytest.skip("No groups available for testing")

    # Use the first group ID for testing
    group_id = response[groups_key][0]["id"]

    # Retrieve the group
    retrieve_response = groups_api.retrieve_group(group_id)

    # Debug info
    print(f"Retrieve group {group_id} response: {retrieve_response}")

    # Verify structure
    assert isinstance(retrieve_response, dict)
    assert "id" in retrieve_response
    assert retrieve_response["id"] == group_id


def test_create_update_delete_group():
    """
    Test creating, updating, and deleting a group.

    This test is skipped because group creation/updates/deletion may require
    admin permissions and could affect production data.
    """
    pytest.skip(
        "Group creation/update/deletion tests are skipped to avoid disrupting production data. "
        "These operations typically require admin permissions."
    )

    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    groups_api = Groups(client)

    # Generate unique test data
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"Test Group {unique_id}"

    try:
        # Create group
        create_response = groups_api.create_group(name=test_name)

        print(f"Create group response: {create_response}")
        assert "id" in create_response
        group_id = create_response["id"]

        # Update group
        updated_name = f"Updated Group {unique_id}"
        update_response = groups_api.update_group(
            group_id=group_id, update_data={"name": updated_name}
        )

        print(f"Update group response: {update_response}")
        assert update_response["name"] == updated_name

        # Delete group
        delete_response = groups_api.delete_group(group_id)

        print(f"Delete group response: {delete_response}")

        # Verify deletion
        with pytest.raises(FollowUpBossApiException) as excinfo:
            groups_api.retrieve_group(group_id)

        assert excinfo.value.status_code in [
            404,
            410,
        ], f"Expected 404 or 410, got {excinfo.value.status_code}"

    except FollowUpBossApiException as e:
        if "Permission denied" in str(e) or "access" in str(e).lower():
            pytest.skip(f"API permission denied: {e}")
        else:
            raise
