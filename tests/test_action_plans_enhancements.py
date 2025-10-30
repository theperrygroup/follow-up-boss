"""
Unit tests for Action Plans enhancements.
"""

import unittest
from unittest.mock import Mock, patch

from follow_up_boss import ActionPlans, FollowUpBossApiClient


class TestActionPlansEnhancements(unittest.TestCase):
    """Test suite for Action Plans enhancement methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Mock(spec=FollowUpBossApiClient)
        self.action_plans = ActionPlans(self.client)

    def test_pause_action_plan_with_reason(self):
        """Test pausing an action plan with a reason."""
        self.action_plans.update_action_plan_assignment = Mock(
            return_value={"id": 123, "status": "paused"}
        )

        result = self.action_plans.pause_action_plan(123, "Communication detected")

        self.action_plans.update_action_plan_assignment.assert_called_once_with(
            123, {"status": "paused", "pauseReason": "Communication detected"}
        )

    def test_pause_action_plan_without_reason(self):
        """Test pausing an action plan without a reason."""
        self.action_plans.update_action_plan_assignment = Mock(
            return_value={"id": 123, "status": "paused"}
        )

        result = self.action_plans.pause_action_plan(123)

        self.action_plans.update_action_plan_assignment.assert_called_once_with(
            123, {"status": "paused"}
        )

    def test_resume_action_plan(self):
        """Test resuming an action plan."""
        self.action_plans.update_action_plan_assignment = Mock(
            return_value={"id": 123, "status": "active"}
        )

        result = self.action_plans.resume_action_plan(123)

        self.action_plans.update_action_plan_assignment.assert_called_once_with(
            123, {"status": "active"}
        )

    def test_pause_all_for_person_success(self):
        """Test pausing all action plans for a person."""
        # Mock list_action_plan_assignments
        self.action_plans.list_action_plan_assignments = Mock(
            return_value={
                "actionPlansPeople": [
                    {"id": 1, "status": "active"},
                    {"id": 2, "status": "active"},
                    {"id": 3, "status": "paused"},  # Already paused
                ]
            }
        )

        # Mock pause_action_plan
        self.action_plans.pause_action_plan = Mock(return_value={"status": "paused"})

        result = self.action_plans.pause_all_for_person(
            person_id=456, reason="Test reason"
        )

        self.assertEqual(result["total_found"], 3)
        self.assertEqual(result["paused_count"], 2)  # Only active ones
        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(len(result["errors"]), 0)

    def test_pause_all_for_person_with_failures(self):
        """Test pausing all action plans with some failures."""
        self.action_plans.list_action_plan_assignments = Mock(
            return_value={
                "actionPlansPeople": [
                    {"id": 1, "status": "active"},
                    {"id": 2, "status": "active"},
                ]
            }
        )

        # First call succeeds, second fails
        self.action_plans.pause_action_plan = Mock(
            side_effect=[
                {"status": "paused"},
                {"error": "Failed to pause"},
            ]
        )

        result = self.action_plans.pause_all_for_person(person_id=456)

        self.assertEqual(result["total_found"], 2)
        self.assertEqual(result["paused_count"], 1)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(len(result["errors"]), 1)

    def test_pause_all_for_person_with_exception(self):
        """Test pausing all action plans when an exception occurs."""
        self.action_plans.list_action_plan_assignments = Mock(
            return_value={
                "actionPlansPeople": [
                    {"id": 1, "status": "active"},
                ]
            }
        )

        # Raise an exception
        self.action_plans.pause_action_plan = Mock(side_effect=Exception("API error"))

        result = self.action_plans.pause_all_for_person(person_id=456)

        self.assertEqual(result["total_found"], 1)
        self.assertEqual(result["paused_count"], 0)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("API error", result["errors"][0])

    def test_pause_all_for_person_only_active_false(self):
        """Test pausing all action plans including non-active ones."""
        self.action_plans.list_action_plan_assignments = Mock(
            return_value={
                "actionPlansPeople": [
                    {"id": 1, "status": "active"},
                    {"id": 2, "status": "paused"},
                ]
            }
        )

        self.action_plans.pause_action_plan = Mock(return_value={"status": "paused"})

        result = self.action_plans.pause_all_for_person(
            person_id=456, only_active=False
        )

        # Should attempt to pause both
        self.assertEqual(result["total_found"], 2)
        self.assertEqual(result["paused_count"], 2)

    def test_pause_all_for_person_missing_id(self):
        """Test pausing action plans when assignment is missing ID."""
        self.action_plans.list_action_plan_assignments = Mock(
            return_value={
                "actionPlansPeople": [
                    {"status": "active"},  # Missing id field
                ]
            }
        )

        result = self.action_plans.pause_all_for_person(person_id=456)

        self.assertEqual(result["total_found"], 1)
        self.assertEqual(result["paused_count"], 0)
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("missing ID", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
