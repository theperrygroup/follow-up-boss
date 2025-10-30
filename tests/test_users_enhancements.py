"""
Unit tests for Users enhancements.
"""

import unittest
from unittest.mock import Mock

from follow_up_boss import FollowUpBossApiClient, Users


class TestUsersEnhancements(unittest.TestCase):
    """Test suite for Users enhancement methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Mock(spec=FollowUpBossApiClient)
        self.users = Users(self.client)

    def test_find_user_by_email_found(self):
        """Test finding a user by email when user exists."""
        self.users.list_users = Mock(
            return_value={
                "users": [
                    {"id": 1, "email": "agent1@example.com", "name": "Agent One"},
                    {"id": 2, "email": "agent2@example.com", "name": "Agent Two"},
                ]
            }
        )

        user = self.users.find_user_by_email("agent2@example.com")

        self.assertIsNotNone(user)
        self.assertEqual(user["id"], 2)
        self.assertEqual(user["name"], "Agent Two")

    def test_find_user_by_email_case_insensitive(self):
        """Test finding a user by email is case-insensitive."""
        self.users.list_users = Mock(
            return_value={
                "users": [
                    {"id": 1, "email": "Agent@Example.com", "name": "Agent One"},
                ]
            }
        )

        user = self.users.find_user_by_email("agent@example.com")

        self.assertIsNotNone(user)
        self.assertEqual(user["id"], 1)

    def test_find_user_by_email_not_found(self):
        """Test finding a user by email when user does not exist."""
        self.users.list_users = Mock(
            return_value={
                "users": [
                    {"id": 1, "email": "agent1@example.com", "name": "Agent One"},
                ]
            }
        )

        user = self.users.find_user_by_email("notfound@example.com")

        self.assertIsNone(user)

    def test_find_user_by_email_empty_email(self):
        """Test finding a user with empty email."""
        user = self.users.find_user_by_email("")

        self.assertIsNone(user)

    def test_find_user_by_email_exception(self):
        """Test finding a user when API raises exception."""
        self.users.list_users = Mock(side_effect=Exception("API Error"))

        user = self.users.find_user_by_email("agent@example.com")

        self.assertIsNone(user)

    def test_get_user_id_by_email_found(self):
        """Test getting user ID by email when user exists."""
        self.users.find_user_by_email = Mock(
            return_value={"id": 123, "email": "agent@example.com", "name": "Agent"}
        )

        user_id = self.users.get_user_id_by_email("agent@example.com")

        self.assertEqual(user_id, 123)

    def test_get_user_id_by_email_not_found(self):
        """Test getting user ID by email when user does not exist."""
        self.users.find_user_by_email = Mock(return_value=None)

        user_id = self.users.get_user_id_by_email("notfound@example.com")

        self.assertIsNone(user_id)

    def test_get_user_id_by_email_no_id_field(self):
        """Test getting user ID when user dict has no id field."""
        self.users.find_user_by_email = Mock(
            return_value={"email": "agent@example.com", "name": "Agent"}
        )

        user_id = self.users.get_user_id_by_email("agent@example.com")

        self.assertIsNone(user_id)

    def test_get_user_id_by_email_string_id(self):
        """Test getting user ID when ID is a string."""
        self.users.find_user_by_email = Mock(
            return_value={
                "id": "456",
                "email": "agent@example.com",
                "name": "Agent",
            }
        )

        user_id = self.users.get_user_id_by_email("agent@example.com")

        self.assertEqual(user_id, 456)


if __name__ == "__main__":
    unittest.main()
