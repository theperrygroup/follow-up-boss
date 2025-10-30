"""
Unit tests for People enhancements.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from follow_up_boss import FollowUpBossApiClient, People


class TestPeopleEnhancements(unittest.TestCase):
    """Test suite for People enhancement methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Mock(spec=FollowUpBossApiClient)
        self.people = People(self.client)

    def test_find_person_id_by_email(self):
        """Test finding a person ID by email."""
        self.people.list_people = Mock(
            return_value={"people": [{"id": 12345, "email": "test@example.com"}]}
        )

        person_id = self.people.find_person_id(email="test@example.com")

        self.assertEqual(person_id, 12345)

    def test_find_person_id_by_phone(self):
        """Test finding a person ID by phone."""
        self.people.list_people = Mock(
            return_value={"people": [{"id": 67890, "phone": "555-1234"}]}
        )

        person_id = self.people.find_person_id(phone="555-1234")

        self.assertEqual(person_id, 67890)

    def test_find_person_id_not_found(self):
        """Test finding a person ID when not found."""
        self.people.list_people = Mock(return_value={"people": []})

        person_id = self.people.find_person_id(email="notfound@example.com")

        self.assertIsNone(person_id)

    def test_find_person_id_no_params(self):
        """Test that ValueError is raised when no params provided."""
        with self.assertRaises(ValueError):
            self.people.find_person_id()

    def test_find_person_id_exception_handling(self):
        """Test find_person_id handles exceptions gracefully."""
        self.people.list_people = Mock(side_effect=Exception("API Error"))

        person_id = self.people.find_person_id(email="test@example.com")

        self.assertIsNone(person_id)

    def test_assign_to_user(self):
        """Test assigning a person to a user."""
        self.people.update_person = Mock(return_value={"id": 123, "assignedTo": 456})

        result = self.people.assign_to_user(person_id=123, user_id=456)

        self.people.update_person.assert_called_once_with(123, {"assignedTo": 456})

    def test_get_person_created_at_success(self):
        """Test getting person creation timestamp."""
        self.people.retrieve_person = Mock(
            return_value={"id": 123, "createdAt": "2025-01-15T10:30:00Z"}
        )

        created_at = self.people.get_person_created_at(123)

        self.assertIsNotNone(created_at)
        self.assertIsInstance(created_at, datetime)
        self.assertEqual(created_at.year, 2025)
        self.assertEqual(created_at.month, 1)
        self.assertEqual(created_at.day, 15)

    def test_get_person_created_at_various_field_names(self):
        """Test getting timestamp from various field names."""
        test_cases = [
            {"createdAt": "2025-01-15T10:30:00Z"},
            {"created": "2025-01-15T10:30:00Z"},
            {"dateCreated": "2025-01-15T10:30:00Z"},
            {"created_at": "2025-01-15T10:30:00Z"},
        ]

        for test_data in test_cases:
            self.people.retrieve_person = Mock(return_value=test_data)
            created_at = self.people.get_person_created_at(123)
            self.assertIsNotNone(created_at)

    def test_get_person_created_at_nested_data(self):
        """Test getting timestamp from nested data field."""
        self.people.retrieve_person = Mock(
            return_value={"data": {"createdAt": "2025-01-15T10:30:00Z"}}
        )

        created_at = self.people.get_person_created_at(123)

        self.assertIsNotNone(created_at)

    def test_get_person_created_at_not_found(self):
        """Test when creation timestamp is not found."""
        self.people.retrieve_person = Mock(return_value={"id": 123, "name": "Test"})

        created_at = self.people.get_person_created_at(123)

        self.assertIsNone(created_at)

    def test_get_person_created_at_exception(self):
        """Test handling of exceptions in get_person_created_at."""
        self.people.retrieve_person = Mock(side_effect=Exception("API Error"))

        created_at = self.people.get_person_created_at(123)

        self.assertIsNone(created_at)

    def test_parse_timestamp_iso8601_with_z(self):
        """Test parsing ISO8601 timestamp with Z suffix."""
        ts = self.people._parse_timestamp("2025-01-15T10:30:00Z")

        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2025)
        self.assertIsNotNone(ts.tzinfo)

    def test_parse_timestamp_iso8601_with_offset(self):
        """Test parsing ISO8601 timestamp with timezone offset."""
        ts = self.people._parse_timestamp("2025-01-15T10:30:00+00:00")

        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2025)

    def test_parse_timestamp_epoch(self):
        """Test parsing Unix epoch timestamp."""
        epoch = 1705318200  # 2025-01-15 10:30:00 UTC
        ts = self.people._parse_timestamp(epoch)

        self.assertIsNotNone(ts)
        self.assertIsNotNone(ts.tzinfo)

    def test_parse_timestamp_nested_dict(self):
        """Test parsing timestamp from nested dictionary."""
        ts = self.people._parse_timestamp({"date": "2025-01-15T10:30:00Z"})

        self.assertIsNotNone(ts)

    def test_parse_timestamp_none(self):
        """Test parsing None value."""
        ts = self.people._parse_timestamp(None)

        self.assertIsNone(ts)

    def test_parse_timestamp_invalid_string(self):
        """Test parsing invalid string."""
        ts = self.people._parse_timestamp("not a timestamp")

        self.assertIsNone(ts)

    def test_add_tags_with_creation_guard_skip(self):
        """Test add_tags skips when within creation guard window."""
        # Mock current time
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(minutes=2)  # Created 2 minutes ago

        self.people.get_person_created_at = Mock(return_value=created_at)

        result = self.people.add_tags(
            person_id=123,
            tags=["New Tag"],
            skip_if_created_within=timedelta(minutes=5),
        )

        # Should skip and return success message
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], 123)
        self.assertIn("Skipped", result["message"])

    def test_add_tags_with_creation_guard_proceed(self):
        """Test add_tags proceeds when outside creation guard window."""
        # Mock current time
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(minutes=10)  # Created 10 minutes ago

        self.people.get_person_created_at = Mock(return_value=created_at)
        self.people.retrieve_person = Mock(return_value={"id": 123, "tags": []})
        self.people.update_person = Mock(return_value={"id": 123, "tags": ["New Tag"]})

        result = self.people.add_tags(
            person_id=123,
            tags=["New Tag"],
            skip_if_created_within=timedelta(minutes=5),
        )

        # Should proceed with tagging
        self.people.update_person.assert_called_once()

    def test_add_tags_with_creation_guard_no_timestamp(self):
        """Test add_tags proceeds when creation timestamp is unavailable."""
        self.people.get_person_created_at = Mock(return_value=None)
        self.people.retrieve_person = Mock(return_value={"id": 123, "tags": []})
        self.people.update_person = Mock(return_value={"id": 123, "tags": ["New Tag"]})

        result = self.people.add_tags(
            person_id=123,
            tags=["New Tag"],
            skip_if_created_within=timedelta(minutes=5),
        )

        # Should proceed when timestamp unavailable
        self.people.update_person.assert_called_once()


if __name__ == "__main__":
    unittest.main()
