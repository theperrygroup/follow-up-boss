"""
Tests for People.add_tags helper.
"""

import os
import uuid
from typing import Any, Dict, List, cast

import pytest

from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.people import People


@pytest.fixture(scope="module")
def people_api() -> People:
    """Create a People API instance using environment-configured client.

    Returns:
        People: API instance configured with env credentials.
    """
    client = FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY"),
    )
    return People(client)


def _create_person_with_tags(api: People, initial_tags: List[str]) -> int:
    """Helper to create a person with initial tags.

    Args:
        api: People API.
        initial_tags: Tags to set on creation.

    Returns:
        int: Newly created person id.
    """
    u = uuid.uuid4().hex[:8]
    person = api.create_person(
        {
            "firstName": "TagTest",
            "lastName": f"Person{u}",
            "emails": [{"value": f"tagtest_{u}@example.com", "type": "work"}],
            "tags": initial_tags,
        }
    )
    person_dict = cast(Dict[str, Any], person)
    return int(person_dict["id"])


@pytest.mark.integration
def test_add_tags_merge_and_dedupe(people_api: People) -> None:
    """Merges provided tags with existing, de-duplicated, preserving order.

    Flow:
    - Create a person with existing tags
    - add_tags with overlapping and new tags
    - Verify final tags contain union without duplicates
    """
    person_id = _create_person_with_tags(people_api, ["Existing A", "Existing B"])
    try:
        updated = people_api.add_tags(
            person_id,
            ["Existing A", "New A", "New B"],
            merge=True,
            case_sensitive=True,
        )
        assert isinstance(updated, dict)
        assert "tags" in updated
        # Order should be existing first, then new ones
        assert updated["tags"] == [
            "Existing A",
            "Existing B",
            "New A",
            "New B",
        ]
    finally:
        people_api.delete_person(person_id)


@pytest.mark.integration
def test_add_tags_replace(people_api: People) -> None:
    """Replaces existing tags when merge=False."""
    person_id = _create_person_with_tags(people_api, ["Old 1", "Old 2"])
    try:
        updated = people_api.add_tags(person_id, ["New 1", "New 2"], merge=False)
        assert isinstance(updated, dict)
        assert updated.get("tags") == ["New 1", "New 2"]
    finally:
        people_api.delete_person(person_id)


@pytest.mark.integration
def test_add_tags_case_insensitive_dedupe(people_api: People) -> None:
    """De-duplicates case-insensitively when case_sensitive=False."""
    person_id = _create_person_with_tags(people_api, ["Tag"])
    try:
        updated = people_api.add_tags(
            person_id, ["tag", "TAG", "TaG"], merge=True, case_sensitive=False
        )
        assert isinstance(updated, dict)
        assert "tags" in updated
        # Should remain single entry for Tag plus preserve original casing where possible
        assert updated["tags"][0] == "Tag"
        assert updated["tags"].count("Tag") == 1
        assert len(updated["tags"]) == 1
    finally:
        people_api.delete_person(person_id)
