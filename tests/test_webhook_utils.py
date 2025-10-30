"""
Unit tests for webhook utilities.
"""

import unittest
from unittest.mock import Mock

from follow_up_boss import FollowUpBossApiClient
from follow_up_boss.webhook_utils import (
    extract_person_id_from_payload,
    get_event_name,
    get_resource_by_collection,
)


class TestWebhookUtils(unittest.TestCase):
    """Test suite for webhook utility functions."""

    def test_get_event_name_from_type(self) -> None:
        """Test extracting event name from 'type' field."""
        payload = {"type": "peopleUpdated"}
        self.assertEqual(get_event_name(payload), "peopleUpdated")

    def test_get_event_name_from_event(self) -> None:
        """Test extracting event name from 'event' field."""
        payload = {"event": "textMessagesCreated"}
        self.assertEqual(get_event_name(payload), "textMessagesCreated")

    def test_get_event_name_from_nested_data(self) -> None:
        """Test extracting event name from nested data field."""
        payload = {"data": {"type": "callsCreated"}}
        self.assertEqual(get_event_name(payload), "callsCreated")

    def test_get_event_name_not_found(self) -> None:
        """Test when event name is not found."""
        payload = {"someOtherField": "value"}
        self.assertEqual(get_event_name(payload), "")

    def test_get_event_name_invalid_payload(self) -> None:
        """Test with invalid payload type."""
        self.assertEqual(get_event_name("not a dict"), "")
        self.assertEqual(get_event_name(None), "")

    def test_extract_person_id_direct_field(self) -> None:
        """Test extracting person ID from direct field."""
        payload = {"personId": 12345}
        person_id = extract_person_id_from_payload(payload)
        self.assertEqual(person_id, 12345)

    def test_extract_person_id_nested_data(self) -> None:
        """Test extracting person ID from nested data field."""
        payload = {"data": {"personId": 67890}}
        person_id = extract_person_id_from_payload(payload)
        self.assertEqual(person_id, 67890)

    def test_extract_person_id_person_object(self) -> None:
        """Test extracting person ID from person object."""
        payload = {"person": {"id": 11111}}
        person_id = extract_person_id_from_payload(payload)
        self.assertEqual(person_id, 11111)

    def test_extract_person_id_from_resource_ids(self) -> None:
        """Test extracting person ID from resourceIds for people events."""
        payload = {"type": "peopleUpdated", "resourceIds": [67890]}
        person_id = extract_person_id_from_payload(payload)
        self.assertEqual(person_id, 67890)

    def test_extract_person_id_from_resource_ids_string(self) -> None:
        """Test extracting person ID from resourceIds with string ID."""
        payload = {"type": "peopleCreated", "resourceIds": ["12345"]}
        person_id = extract_person_id_from_payload(payload)
        self.assertEqual(person_id, 12345)

    def test_extract_person_id_from_uri(self) -> None:
        """Test extracting person ID from URI query parameter."""
        payload = {"uri": "/api/people?id=99999"}
        person_id = extract_person_id_from_payload(payload)
        self.assertEqual(person_id, 99999)

    def test_extract_person_id_not_found(self) -> None:
        """Test when person ID cannot be extracted."""
        payload = {"someOtherField": "value"}
        person_id = extract_person_id_from_payload(payload)
        self.assertIsNone(person_id)

    def test_extract_person_id_with_client_text_message(self) -> None:
        """Test extracting person ID by fetching text message resource."""
        client = Mock(spec=FollowUpBossApiClient)
        payload = {"type": "textMessagesCreated", "resourceIds": [123]}

        # Mock the TextMessages class (imported inside the function)
        with unittest.mock.patch(
            "follow_up_boss.text_messages.TextMessages"
        ) as MockTextMessages:
            mock_instance = MockTextMessages.return_value
            mock_instance.retrieve_text_message.return_value = {"personId": 456}

            person_id = extract_person_id_from_payload(payload, client)

            self.assertEqual(person_id, 456)
            mock_instance.retrieve_text_message.assert_called_once_with(123)

    def test_extract_person_id_resource_fetch_failure(self) -> None:
        """Test when resource fetch fails."""
        client = Mock(spec=FollowUpBossApiClient)
        payload = {"type": "textMessagesCreated", "resourceIds": [123]}

        # Mock the TextMessages class to raise exception
        with unittest.mock.patch(
            "follow_up_boss.text_messages.TextMessages"
        ) as MockTextMessages:
            mock_instance = MockTextMessages.return_value
            mock_instance.retrieve_text_message.side_effect = Exception("API Error")

            person_id = extract_person_id_from_payload(payload, client)

            self.assertIsNone(person_id)

    def test_get_resource_by_collection_text_messages(self) -> None:
        """Test fetching text message resource by collection."""
        client = Mock(spec=FollowUpBossApiClient)

        with unittest.mock.patch(
            "follow_up_boss.text_messages.TextMessages"
        ) as MockTextMessages:
            mock_instance = MockTextMessages.return_value
            mock_instance.retrieve_text_message.return_value = {
                "id": 123,
                "message": "Test",
            }

            resource = get_resource_by_collection(client, "textMessages", 123)

            self.assertIsNotNone(resource)
            self.assertEqual(resource["id"], 123)

    def test_get_resource_by_collection_notes(self) -> None:
        """Test fetching note resource by collection."""
        client = Mock(spec=FollowUpBossApiClient)

        with unittest.mock.patch("follow_up_boss.notes.Notes") as MockNotes:
            mock_instance = MockNotes.return_value
            mock_instance.retrieve_note.return_value = {"id": 456, "note": "Test note"}

            resource = get_resource_by_collection(client, "notes", 456)

            self.assertIsNotNone(resource)
            self.assertEqual(resource["id"], 456)

    def test_get_resource_by_collection_unknown(self) -> None:
        """Test fetching resource with unknown collection."""
        client = Mock(spec=FollowUpBossApiClient)

        resource = get_resource_by_collection(client, "unknown", 123)

        self.assertIsNone(resource)

    def test_get_resource_by_collection_exception(self) -> None:
        """Test handling exception when fetching resource."""
        client = Mock(spec=FollowUpBossApiClient)

        with unittest.mock.patch(
            "follow_up_boss.text_messages.TextMessages"
        ) as MockTextMessages:
            mock_instance = MockTextMessages.return_value
            mock_instance.retrieve_text_message.side_effect = Exception("API Error")

            resource = get_resource_by_collection(client, "textMessages", 123)

            self.assertIsNone(resource)


if __name__ == "__main__":
    unittest.main()
