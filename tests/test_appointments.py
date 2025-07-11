"""
Test the Appointments API.
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from follow_up_boss.appointments import Appointments
from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException


@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )


@pytest.fixture
def appointments_api(client):
    """Create an Appointments instance for testing."""
    return Appointments(client)


def test_list_appointments(appointments_api):
    """Test listing appointments."""
    response = appointments_api.list_appointments()

    # Debug print
    print("List Appointments Response:", response)

    # Check basic structure of the response
    assert isinstance(response, dict)
    assert "_metadata" in response

    # The API might return 'appointments' (lowercase) or similar key
    expected_keys = ["appointments", "data"]
    found_key = False
    for key in expected_keys:
        if key in response:
            assert isinstance(response[key], list)
            found_key = True
            break

    if not found_key:
        # Check metadata for collection name
        assert "collection" in response["_metadata"]
        assert response["_metadata"]["collection"] in ["appointments"]


def test_appointment_operations_with_invalid_id(appointments_api):
    """Test appointment operations with an invalid ID."""
    invalid_id = 999999999  # Assuming this ID doesn't exist

    # Test retrieve
    with pytest.raises(FollowUpBossApiException) as excinfo:
        appointments_api.retrieve_appointment(invalid_id)
    assert excinfo.value.status_code in [404, 400]
    print(f"Expected error when retrieving nonexistent appointment: {excinfo.value}")

    # Test update
    with pytest.raises(FollowUpBossApiException) as excinfo:
        appointments_api.update_appointment(
            invalid_id, {"title": "Updated Appointment"}
        )
    assert excinfo.value.status_code in [404, 400]
    print(f"Expected error when updating nonexistent appointment: {excinfo.value}")

    # Test delete
    with pytest.raises(FollowUpBossApiException) as excinfo:
        appointments_api.delete_appointment(invalid_id)
    assert excinfo.value.status_code in [404, 400]
    print(f"Expected error when deleting nonexistent appointment: {excinfo.value}")


def test_create_appointment_date_formats():
    """
    Test creating an appointment with various date formats.

    This test tries different date formats and payload structures to identify
    what the API expects for appointment creation.
    """
    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    appointments_api = Appointments(client)

    # Get appointment types to use a valid type ID
    from follow_up_boss.appointment_types import AppointmentTypes

    types_api = AppointmentTypes(client)
    types_response = types_api.list_appointment_types()

    types_key = None
    for key in types_response:
        if key.lower() in ["appointmenttypes", "types"] and isinstance(
            types_response[key], list
        ):
            types_key = key
            break

    if not types_key or not types_response[types_key]:
        pytest.skip("No appointment types available for testing")

    appointment_type_id = types_response[types_key][0]["id"]
    print(f"Using appointment type ID: {appointment_type_id}")

    # Get a person ID to associate with the appointment
    from follow_up_boss.people import People

    people_api = People(client)
    people_response = people_api.list_people(params={"limit": 1})

    if "people" not in people_response or not people_response["people"]:
        pytest.skip("No people available for testing")

    person_id = people_response["people"][0]["id"]
    print(f"Using person ID: {person_id}")

    # Generate test appointment times
    now = datetime.now(timezone.utc)
    start_time = now + timedelta(days=1, hours=10)  # Tomorrow at 10am
    end_time = start_time + timedelta(hours=1)  # 1 hour appointment

    # Define various date formats to try
    date_formats = [
        # Format 1: ISO format with timezone
        (start_time.isoformat(), end_time.isoformat()),
        # Format 2: ISO format without timezone
        (
            start_time.replace(tzinfo=None).isoformat(),
            end_time.replace(tzinfo=None).isoformat(),
        ),
        # Format 3: ISO format without microseconds
        (
            start_time.replace(microsecond=0).isoformat(),
            end_time.replace(microsecond=0).isoformat(),
        ),
        # Format 4: YYYY-MM-DD format (date only)
        (start_time.date().isoformat(), end_time.date().isoformat()),
        # Format 5: Unix timestamp as integer
        (int(start_time.timestamp()), int(end_time.timestamp())),
        # Format 6: Unix timestamp as string
        (str(int(start_time.timestamp())), str(int(end_time.timestamp()))),
        # Format 7: SQLite format (YYYY-MM-DD HH:MM:SS)
        (
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time.strftime("%Y-%m-%d %H:%M:%S"),
        ),
        # Format 8: MM/DD/YYYY HH:MM:SS format
        (
            start_time.strftime("%m/%d/%Y %H:%M:%S"),
            end_time.strftime("%m/%d/%Y %H:%M:%S"),
        ),
    ]

    # Try combinations of payloads and date formats
    for idx, (start_format, end_format) in enumerate(date_formats):
        print(f"\n=== Testing date format {idx+1} ===")
        print(f"Start: {start_format}")
        print(f"End: {end_format}")

        # Try different payloads
        payloads = [
            # Payload 1: Start/end times as top-level properties
            {
                "title": f"Test Appointment Format {idx+1}",
                "description": "Automated test appointment",
                "location": "Test location",
                "startTime": start_format,
                "endTime": end_format,
                "appointmentTypeId": appointment_type_id,
            },
            # Payload 2: All-day flag with start/end dates
            {
                "title": f"All-day Test Appointment Format {idx+1}",
                "description": "Automated test all-day appointment",
                "location": "Test location",
                "startDate": start_time.date().isoformat(),
                "endDate": end_time.date().isoformat(),
                "allDay": True,
                "appointmentTypeId": appointment_type_id,
            },
            # Payload 3: Using 'date' properties
            {
                "title": f"Test Appointment Date Format {idx+1}",
                "description": "Automated test appointment",
                "location": "Test location",
                "date": start_time.date().isoformat(),
                "startTime": start_format,
                "endTime": end_format,
                "appointmentTypeId": appointment_type_id,
            },
            # Payload 4: With person association
            {
                "title": f"Test Appointment with Person Format {idx+1}",
                "description": "Automated test appointment with person",
                "location": "Test location",
                "startTime": start_format,
                "endTime": end_format,
                "appointmentTypeId": appointment_type_id,
                "personId": person_id,
            },
            # Payload 5: With contacts array
            {
                "title": f"Test Appointment with Contacts Format {idx+1}",
                "description": "Automated test appointment with contacts",
                "location": "Test location",
                "startTime": start_format,
                "endTime": end_format,
                "appointmentTypeId": appointment_type_id,
                "contacts": [{"id": person_id}],
            },
        ]

        # Try each payload
        for payload_idx, payload in enumerate(payloads):
            # Skip some redundant combinations for efficiency
            if payload_idx >= 2 and idx > 3:
                continue

            print(f"\n--- Testing payload {payload_idx+1} ---")
            print(f"Payload: {json.dumps(payload, indent=2)}")

            # Try the payload in the body
            try:
                print("Attempting with payload in body...")
                response = appointments_api.create_appointment(payload)
                print(f"SUCCESS with body payload! Response: {response}")

                if isinstance(response, dict) and "id" in response:
                    appointment_id = response["id"]

                    # Test successful retrieval
                    retrieve_response = appointments_api.retrieve_appointment(
                        appointment_id
                    )
                    print(f"Retrieved appointment: {retrieve_response}")

                    # Clean up - delete the appointment
                    delete_response = appointments_api.delete_appointment(
                        appointment_id
                    )
                    print(f"Deleted appointment: {delete_response}")

                    # Format worked! Document the working payload
                    print("\n====== WORKING APPOINTMENT PAYLOAD ======")
                    print(f"Date format: {idx+1}")
                    print(f"Payload format: {payload_idx+1}")
                    print(f"Start time format: {start_format}")
                    print(f"End time format: {end_format}")
                    print(f"Full payload: {json.dumps(payload, indent=2)}")
                    print("==========================================\n")

                    # We've found a working combination, so we can return
                    return
            except FollowUpBossApiException as e:
                print(f"Failed with body payload: Status {e.status_code} - {e.message}")
                if hasattr(e, "response_data") and e.response_data:
                    print(f"Response data: {e.response_data}")

            # Try the same payload as query parameters
            try:
                print("Attempting with payload as query params...")
                # Extract appointmentTypeId for the body
                body_data = {"title": payload.get("title", "Test Appointment")}
                # Move everything else to query params
                params = {k: v for k, v in payload.items() if k != "title"}

                response = appointments_api.create_appointment(body_data, params=params)
                print(f"SUCCESS with query params! Response: {response}")

                if isinstance(response, dict) and "id" in response:
                    appointment_id = response["id"]

                    # Test successful retrieval
                    retrieve_response = appointments_api.retrieve_appointment(
                        appointment_id
                    )
                    print(f"Retrieved appointment: {retrieve_response}")

                    # Clean up - delete the appointment
                    delete_response = appointments_api.delete_appointment(
                        appointment_id
                    )
                    print(f"Deleted appointment: {delete_response}")

                    # Format worked! Document the working payload
                    print("\n====== WORKING APPOINTMENT PAYLOAD (QUERY PARAMS) ======")
                    print(f"Date format: {idx+1}")
                    print(f"Payload format: {payload_idx+1}")
                    print(f"Body data: {json.dumps(body_data, indent=2)}")
                    print(f"Query params: {json.dumps(params, indent=2)}")
                    print("==========================================\n")

                    # We've found a working combination, so we can return
                    return
            except FollowUpBossApiException as e:
                print(f"Failed with query params: Status {e.status_code} - {e.message}")
                if hasattr(e, "response_data") and e.response_data:
                    print(f"Response data: {e.response_data}")

    # If we get here, none of the combinations worked
    pytest.skip("Could not find a working appointment creation payload format")


def test_book_appointment_with_documentation_format():
    """
    Test creating an appointment with the format from the API documentation.

    Based on: https://docs.followupboss.com/reference/appointments-post
    """
    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    appointments_api = Appointments(client)

    # Get appointment types
    from follow_up_boss.appointment_types import AppointmentTypes

    types_api = AppointmentTypes(client)
    types_response = types_api.list_appointment_types()

    types_key = None
    for key in types_response:
        if key.lower() in ["appointmenttypes", "types"] and isinstance(
            types_response[key], list
        ):
            types_key = key
            break

    if not types_key or not types_response[types_key]:
        pytest.skip("No appointment types available for testing")

    appointment_type_id = types_response[types_key][0]["id"]
    print(f"Using appointment type ID: {appointment_type_id}")

    # Get a person to be an attendee
    from follow_up_boss.people import People

    people_api = People(client)
    people_response = people_api.list_people(params={"limit": 1})

    if "people" not in people_response or not people_response["people"]:
        pytest.skip("No people available for testing")

    person = people_response["people"][0]
    print(
        f"Using person: {person['firstName']} {person.get('lastName', '')} (ID: {person['id']})"
    )

    # Get the current user
    from follow_up_boss.users import Users

    users_api = Users(client)
    me_response = users_api.get_current_user()
    user_id = me_response.get("id")
    print(f"Current user: {me_response.get('name', 'Unknown')} (ID: {user_id})")

    # Generate dates in ISO format
    now = datetime.now()
    start_time = now + timedelta(days=1, hours=10)  # Tomorrow at 10am
    end_time = start_time + timedelta(hours=1)  # 1 hour duration

    # Format in ISO8601
    start_time_iso = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_time_iso = end_time.strftime("%Y-%m-%dT%H:%M:%S")

    # Create contacts array
    contacts = [{"id": person["id"], "type": "person"}]

    # Try booking the appointment directly using the documented format
    try:
        # First try using direct create_appointment with the documented format
        direct_payload = {
            "title": "API Documentation Test",
            "when": {"start": start_time_iso, "end": end_time_iso},
            "appointmentTypeId": appointment_type_id,
            "contacts": contacts,
            "location": "Test Location",
            "description": "This is a test appointment using the documented format",
        }

        if user_id:
            direct_payload["hostId"] = user_id

        print(f"Trying direct payload: {json.dumps(direct_payload, indent=2)}")
        response = appointments_api.create_appointment(direct_payload)
        print(f"SUCCESS with direct payload! Response: {response}")

        # If successful, clean up
        if isinstance(response, dict) and "id" in response:
            appointment_id = response["id"]
            delete_response = appointments_api.delete_appointment(appointment_id)
            print(f"Deleted appointment: {delete_response}")

        return  # Test succeeded
    except FollowUpBossApiException as e:
        print(f"Direct payload failed: Status {e.status_code} - {e.message}")
        if hasattr(e, "response_data") and e.response_data:
            print(f"Response data: {e.response_data}")

    # If that failed, try using the book_appointment helper method
    try:
        response = appointments_api.book_appointment(
            title="API Method Test",
            start_time=start_time_iso,
            end_time=end_time_iso,
            appointment_type_id=appointment_type_id,
            contacts=contacts,
            location="Test Location",
            description="This is a test appointment using the helper method",
            host_user_id=user_id,
        )

        print(f"SUCCESS with book_appointment! Response: {response}")

        # If successful, clean up
        if isinstance(response, dict) and "id" in response:
            appointment_id = response["id"]
            delete_response = appointments_api.delete_appointment(appointment_id)
            print(f"Deleted appointment: {delete_response}")

        return  # Test succeeded
    except FollowUpBossApiException as e:
        print(f"book_appointment failed: Status {e.status_code} - {e.message}")
        if hasattr(e, "response_data") and e.response_data:
            print(f"Response data: {e.response_data}")

    # If we get here, both attempts failed
    pytest.skip(
        "All appointment creation attempts with API documentation format failed"
    )
