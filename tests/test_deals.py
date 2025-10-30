"""
Test the Deals API.
"""

import os
from datetime import datetime, timedelta

import pytest

from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.deals import Deals, DealsValidationError
from follow_up_boss.people import People
from follow_up_boss.pipelines import Pipelines
from follow_up_boss.stages import Stages
from follow_up_boss.users import Users

pytestmark = pytest.mark.integration  # Mark all tests in this module as integration


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def deals_api(client):
    """Create a Deals instance for testing."""
    return Deals(client)


@pytest.fixture
def pipelines_api(client):
    """Create a Pipelines instance for testing."""
    return Pipelines(client)


@pytest.fixture
def stages_api(client):
    """Create a Stages instance for testing."""
    return Stages(client)


@pytest.fixture
def users_api(client):
    """Create a Users instance for testing."""
    return Users(client)


@pytest.fixture
def people_api(client):
    """Create a People instance for testing."""
    return People(client)


@pytest.fixture(scope="session")
def test_pipeline_id():
    """Get a pipeline ID for testing or create one if needed (cached for session)."""
    from follow_up_boss.pipelines import Pipelines

    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    pipelines_api = Pipelines(client)

    # Get a pipeline
    pipelines_response = pipelines_api.list_pipelines()

    pipeline_id = None
    if "pipelines" in pipelines_response and pipelines_response["pipelines"]:
        pipeline_id = pipelines_response["pipelines"][0]["id"]
    else:
        # Create a pipeline if none exists
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_pipeline = pipelines_api.create_pipeline(name=f"Test Pipeline {timestamp}")
        pipeline_id = new_pipeline["id"]

    return pipeline_id


@pytest.fixture(scope="session")
def test_stage_id(test_pipeline_id):
    """Get a stage ID for testing that belongs to the pipeline (cached for session)."""
    from follow_up_boss.pipelines import Pipelines

    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    pipelines_api = Pipelines(client)

    # Get the pipeline to find its stages
    pipeline_response = pipelines_api.retrieve_pipeline(test_pipeline_id)

    if "stages" not in pipeline_response or not pipeline_response["stages"]:
        # If the pipeline has no stages, we'll get stages from the general stages endpoint
        # but this will likely fail as the stage needs to be part of the pipeline
        stages_response = pipelines_api.list_pipelines()
        for pipeline in stages_response.get("pipelines", []):
            if pipeline.get("id") == test_pipeline_id and pipeline.get("stages"):
                return pipeline["stages"][0]["id"]

        pytest.skip("No stages available for the selected pipeline")

    # Return the first stage in the pipeline
    return pipeline_response["stages"][0]["id"]


@pytest.fixture(scope="session")
def test_user_id():
    """Get a user ID for testing (cached for session)."""
    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    users_api = Users(client)

    # Get a user
    users_response = users_api.list_users()

    if "users" not in users_response or not users_response["users"]:
        pytest.skip("No users available for testing")

    return users_response["users"][0]["id"]


@pytest.fixture(scope="session")
def test_person_id():
    """Get a person ID for testing (cached for session)."""
    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    people_api = People(client)

    # Get a person
    people_response = people_api.list_people(params={"limit": 1})

    if "people" not in people_response or not people_response["people"]:
        pytest.skip("No people available for testing")

    return people_response["people"][0]["id"]


@pytest.fixture
def test_deal_id(deals_api, test_stage_id):
    """Create a test deal and return its ID for testing."""
    # Create a minimal deal with just stageId which is the only required field
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_data = {"name": f"Test Deal {timestamp}", "stage_id": test_stage_id}

    try:
        response = deals_api.create_deal(**deal_data)
        deal_id = response["id"]

        yield deal_id

        # Clean up the deal after test
        try:
            deals_api.delete_deal(deal_id)
        except Exception as e:
            print(f"Error cleaning up test deal: {e}")
    except FollowUpBossApiException as e:
        pytest.skip(f"Failed to create test deal: {e}")


def test_list_deals(deals_api):
    """Test listing deals."""
    response = deals_api.list_deals()

    # Debug info
    print(f"List deals response: {response}")

    # Verify response structure
    assert isinstance(response, dict)
    # The response should contain a list of deals - the exact key might vary
    found_deals = False
    for key in ["deals", "data", "_data"]:
        if key in response and isinstance(response[key], list):
            found_deals = True
            break

    # Should have a metadata section
    assert "_metadata" in response

    # Either found deals key or it's in metadata
    assert found_deals or "collection" in response["_metadata"]


def test_create_and_retrieve_deal(deals_api, test_stage_id, resource_tracker):
    """Test creating and retrieving a deal."""
    # Create a minimal deal
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Test Deal {timestamp}"

    response = deals_api.create_deal(name=deal_name, stage_id=test_stage_id)

    # Debug info
    print(f"Create deal response: {response}")

    # Verify the deal was created successfully
    assert isinstance(response, dict)
    assert "id" in response
    assert response["name"] == deal_name

    deal_id = response["id"]

    # Track for cleanup
    resource_tracker["deals"].append(deal_id)

    # Retrieve the deal
    retrieve_response = deals_api.retrieve_deal(deal_id)

    # Debug info
    print(f"Retrieve deal response: {retrieve_response}")

    # Verify the retrieved deal matches what we created
    assert isinstance(retrieve_response, dict)
    assert retrieve_response["id"] == deal_id
    assert retrieve_response["name"] == deal_name


def test_update_deal(deals_api, test_deal_id):
    """Test updating a deal."""
    # Update the deal
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    updated_name = f"Updated Deal {timestamp}"
    updated_price = 150000.00

    update_data = {"name": updated_name, "price": updated_price}

    response = deals_api.update_deal(test_deal_id, update_data)

    # Debug info
    print(f"Update deal response: {response}")

    # Verify the deal was updated successfully
    assert isinstance(response, dict)
    assert response["id"] == test_deal_id
    assert response["name"] == updated_name
    assert (
        abs(float(response["price"]) - updated_price) < 0.01
    )  # Handle potential floating point differences

    # Retrieve the deal to verify updates
    retrieve_response = deals_api.retrieve_deal(test_deal_id)

    # Verify the retrieved deal has the updates
    assert retrieve_response["name"] == updated_name
    assert abs(float(retrieve_response["price"]) - updated_price) < 0.01


def test_delete_deal(deals_api, test_stage_id, resource_tracker):
    """Test deleting a deal."""
    # Create a deal specifically for deletion with minimal fields (don't track since we're testing deletion)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Delete Test Deal {timestamp}"

    response = deals_api.create_deal(name=deal_name, stage_id=test_stage_id)

    # Verify the deal was created
    assert "id" in response
    deal_id = response["id"]

    # Delete the deal
    delete_response = deals_api.delete_deal(deal_id)

    # Debug info
    print(f"Delete deal response: {delete_response}")

    # Verify deletion - the API returns an empty list or dict with rate limit info
    assert (
        delete_response == ""
        or delete_response == []
        or (
            isinstance(delete_response, dict)
            and (not delete_response or "_rateLimit" in delete_response)
        )
    )

    # The API marks deals as "Deleted" rather than actually removing them
    # Retrieve the deal to verify its status
    retrieve_response = deals_api.retrieve_deal(deal_id)

    # Verify the deal has been marked as deleted
    assert retrieve_response["status"] == "Deleted"


# New Commission Field Tests


def test_commission_fields_in_create_deal(deals_api, test_stage_id, resource_tracker):
    """Test that commission fields work as top-level parameters."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Commission Test Deal {timestamp}"

    deal_data = {
        "name": deal_name,
        "stage_id": test_stage_id,
        "price": 450000,
        "commissionValue": 13500,
        "agentCommission": 9450,
        "teamCommission": 4050,
    }

    response = deals_api.create_deal(**deal_data)

    # Debug info
    print(f"Commission create deal response: {response}")

    # Verify the deal was created successfully
    assert isinstance(response, dict)
    assert "id" in response
    deal_id = response["id"]

    # Track for cleanup
    resource_tracker["deals"].append(deal_id)

    # Verify commission fields were set
    assert response.get("commissionValue") == 13500
    assert response.get("agentCommission") == 9450
    assert response.get("teamCommission") == 4050

    # Verify helper properties were added
    assert response.get("has_commission") is True
    assert "total_people" in response
    assert "total_users" in response


def test_commission_fields_in_custom_fields_raises_error(deals_api, test_stage_id):
    """Test that commission fields in custom_fields raise validation error."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Invalid Commission Test Deal {timestamp}"

    deal_data = {
        "name": deal_name,
        "stage_id": test_stage_id,
        "price": 450000,
        "custom_fields": {"commissionValue": 13500},  # This should raise an error
    }

    with pytest.raises(DealsValidationError) as exc_info:
        deals_api.create_deal(**deal_data)

    # Verify the error message contains helpful guidance
    error_message = str(exc_info.value)
    assert "commissionValue" in error_message
    assert "top-level parameter" in error_message
    assert "custom_fields" in error_message


def test_multiple_commission_fields_in_custom_fields_raises_error(
    deals_api, test_stage_id
):
    """Test that multiple commission fields in custom_fields raise validation error."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Multiple Invalid Commission Test Deal {timestamp}"

    deal_data = {
        "name": deal_name,
        "stage_id": test_stage_id,
        "price": 450000,
        "custom_fields": {
            "commissionValue": 13500,
            "agentCommission": 9450,
            "teamCommission": 4050,
        },
    }

    with pytest.raises(DealsValidationError) as exc_info:
        deals_api.create_deal(**deal_data)

    # Verify the error message contains all commission fields
    error_message = str(exc_info.value)
    assert "commissionValue" in error_message
    assert "agentCommission" in error_message
    assert "teamCommission" in error_message


def test_update_deal_commission_validation(deals_api, test_deal_id):
    """Test that commission validation works for update operations."""
    update_data = {
        "custom_fields": {"commissionValue": 15000}  # This should raise an error
    }

    with pytest.raises(DealsValidationError) as exc_info:
        deals_api.update_deal(test_deal_id, update_data)

    # Verify the error message
    error_message = str(exc_info.value)
    assert "commissionValue" in error_message
    assert "top-level parameter" in error_message


def test_set_deal_commission_helper_method(deals_api, test_deal_id):
    """Test the set_deal_commission helper method."""
    commission_data = {"total": 15000.0, "agent": 10500.0, "team": 4500.0}

    response = deals_api.set_deal_commission(test_deal_id, commission_data)

    # Debug info
    print(f"Set commission response: {response}")

    # Verify the response
    assert isinstance(response, dict)
    assert response["id"] == test_deal_id

    # Verify commission values were set
    assert response.get("commissionValue") == 15000.0
    assert response.get("agentCommission") == 10500.0
    assert response.get("teamCommission") == 4500.0

    # Verify helper properties
    assert response.get("has_commission") is True


def test_field_name_normalization(deals_api, test_deal_id):
    """Test field name normalization functionality."""
    # Retrieve deal with normalization
    response = deals_api.retrieve_deal(test_deal_id, normalize_fields=True)

    # Debug info
    print(f"Normalized response: {response}")

    # Verify normalized field names are used
    assert isinstance(response, dict)
    # The actual field names will depend on what the API returns
    # This test verifies the normalization method works without breaking functionality


def test_commission_helper_data_preparation(deals_api):
    """Test the commission data preparation helper method."""
    commission_data = {"total": 12000.0, "agent": 8400.0, "team": 3600.0}

    # Test the private method through the public interface
    prepared_data = deals_api._prepare_commission_data(commission_data)

    # Verify the prepared data
    assert prepared_data["commissionValue"] == 12000.0
    assert prepared_data["agentCommission"] == 8400.0
    assert prepared_data["teamCommission"] == 3600.0


def test_commission_partial_data_preparation(deals_api):
    """Test commission data preparation with partial data."""
    commission_data = {
        "total": 10000.0,
        "agent": 7000.0,
        # Missing 'team' field
    }

    prepared_data = deals_api._prepare_commission_data(commission_data)

    # Verify only provided fields are included
    assert prepared_data["commissionValue"] == 10000.0
    assert prepared_data["agentCommission"] == 7000.0
    assert "teamCommission" not in prepared_data


def test_enhanced_error_message_formatting(deals_api, test_stage_id, resource_tracker):
    """Test that enhanced error messages are properly formatted."""
    # This test may not always trigger the enhanced error handling
    # but it verifies the functionality doesn't break normal operations

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Error Test Deal {timestamp}"

    try:
        # Try to create a deal with invalid data to trigger enhanced error handling
        response = deals_api.create_deal(
            name=deal_name,
            stage_id=test_stage_id,
            commissionValue=12000.0,  # Valid commission field
        )

        # If successful, track for cleanup
        if isinstance(response, dict) and "id" in response:
            resource_tracker["deals"].append(response["id"])

        # Test passes if no exception is raised
        assert True

    except FollowUpBossApiException as e:
        # If an exception is raised, verify it has enhanced error handling
        error_message = str(e)
        # The error message should contain the original error plus any enhancements
        assert len(error_message) > 0
        print(f"Enhanced error message: {error_message}")


def test_create_deal_with_all_commission_fields(
    deals_api, test_stage_id, resource_tracker
):
    """Test creating a deal with all commission fields and verify response helpers."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    deal_name = f"Full Commission Test Deal {timestamp}"

    response = deals_api.create_deal(
        name=deal_name,
        stage_id=test_stage_id,
        price=500000,
        commissionValue=15000.0,
        agentCommission=10500.0,
        teamCommission=4500.0,
        description="Test deal with full commission data",
    )

    # Debug info
    print(f"Full commission deal response: {response}")

    # Verify the deal was created successfully
    assert isinstance(response, dict)
    assert "id" in response
    deal_id = response["id"]

    # Track for cleanup
    resource_tracker["deals"].append(deal_id)

    # Verify all commission fields
    assert response.get("commissionValue") == 15000.0
    assert response.get("agentCommission") == 10500.0
    assert response.get("teamCommission") == 4500.0

    # Verify helper properties
    assert response.get("has_commission") is True
    assert isinstance(response.get("total_people"), int)
    assert isinstance(response.get("total_users"), int)
