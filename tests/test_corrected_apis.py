#!/usr/bin/env python3
"""
Test script to validate corrected API calls based on discovered method signatures.
"""

import sys
import time

sys.path.insert(0, ".")

from follow_up_boss.appointments import Appointments
from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.custom_fields import CustomFields
from follow_up_boss.email_templates import EmailTemplates
from follow_up_boss.people import People
from follow_up_boss.tasks import Tasks


def test_corrected_apis():
    client = FollowUpBossApiClient()
    person_id = None

    # Test 1: People API with correct format
    print("=== Testing People API ===")
    people_api = People(client)
    person_data = {
        "firstName": "Test",
        "lastName": "PersonCorrect",
        "emails": [
            {"value": f"test{int(time.time())}@example.com", "type": "Personal"}
        ],
        "source": "API Test",
    }
    try:
        result = people_api.create_person(person_data)
        print(f'✅ People API Success: Created person ID {result.get("id")}')
        person_id = result.get("id")
    except Exception as e:
        print(f"❌ People API Failed: {e}")
        person_id = None

    # Test 2: Tasks API with correct parameters
    print("\n=== Testing Tasks API ===")
    tasks_api = Tasks(client)
    try:
        result = tasks_api.create_task(
            name="Test Task from API",
            person_id=person_id if person_id else 779,
            due_date="2025-05-24T10:00:00Z",
            details="Test task details",
        )
        print(f'✅ Tasks API Success: Created task ID {result.get("id")}')
    except Exception as e:
        print(f"❌ Tasks API Failed: {e}")

    # Test 3: Appointments API with dict parameter
    print("\n=== Testing Appointments API ===")
    appointments_api = Appointments(client)
    appointment_data = {
        "personId": person_id if person_id else 779,
        "startDate": "2025-05-24T10:00:00Z",
        "endDate": "2025-05-24T11:00:00Z",
        "title": "Test Appointment",
    }
    try:
        result = appointments_api.create_appointment(appointment_data)
        print(f'✅ Appointments API Success: Created appointment ID {result.get("id")}')
    except Exception as e:
        print(f"❌ Appointments API Failed: {e}")

    # Test 4: Email Templates API with correct parameters
    print("\n=== Testing Email Templates API ===")
    templates_api = EmailTemplates(client)
    try:
        result = templates_api.create_email_template(
            name=f"Test Template {int(time.time())}",
            subject="Test Subject",
            body="<html><body>Test email template</body></html>",
        )
        print(f'✅ Email Templates API Success: Created template ID {result.get("id")}')
    except Exception as e:
        print(f"❌ Email Templates API Failed: {e}")

    # Test 5: Custom Fields API with research on valid types
    print("\n=== Testing Custom Fields API ===")
    fields_api = CustomFields(client)

    # Try different field types to find valid ones
    field_types_to_try = [
        "text",
        "number",
        "date",
        "dropdown",
        "singlelinetext",
        "multilinetext",
    ]

    for field_type in field_types_to_try:
        try:
            print(f"   Trying field type: {field_type}")
            result = fields_api.create_custom_field(
                name=f"Test Field {field_type} {int(time.time())}", type=field_type
            )
            print(
                f'✅ Custom Fields API Success with type "{field_type}": Created field ID {result.get("id")}'
            )
            break
        except Exception as e:
            print(f'   ❌ Field type "{field_type}" failed: {e}')
            continue


if __name__ == "__main__":
    test_corrected_apis()
