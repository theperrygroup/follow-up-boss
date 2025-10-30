from typing import Any, Dict, List

import pytest

from follow_up_boss.people import People


@pytest.mark.unit
def test_list_people_enriches_metadata(mock_client: Any) -> None:
    people_api = People(mock_client)

    mock_client._get.return_value = {
        "people": [{"id": 1}],
        "_metadata": {"collection": "people", "limit": 1},
    }

    resp = people_api.list_people({"limit": 1, "listId": 123})
    assert resp["people"] == [{"id": 1}]
    meta = resp.get("_metadata", {})
    assert meta.get("limit") == 1
    assert meta.get("listId") == 123


@pytest.mark.unit
def test_list_people_next_uses_absolute_link(mock_client: Any) -> None:
    people_api = People(mock_client)

    page2: Dict[str, Any] = {
        "people": [{"id": 2}, {"id": 3}],
        "_metadata": {"collection": "people"},
    }

    mock_client.get_absolute.return_value = page2

    out = people_api.list_people_next("https://api.followupboss.com/v1/people?next=TOKEN")
    assert [p["id"] for p in out.get("people", [])] == [2, 3]
    mock_client.get_absolute.assert_called_once()


@pytest.mark.unit
def test_iter_people_traverses_nextlink(mock_client: Any) -> None:
    people_api = People(mock_client)

    # First page via list_people
    page1: Dict[str, Any] = {
        "people": [{"id": 1}],
        "_metadata": {"nextLink": "https://api.followupboss.com/v1/people?next=TOKEN1"},
    }

    # Subsequent pages via get_absolute
    page2: Dict[str, Any] = {
        "people": [{"id": 2}],
        "_metadata": {"nextLink": "https://api.followupboss.com/v1/people?next=TOKEN2"},
    }
    page3: Dict[str, Any] = {"people": [{"id": 3}], "_metadata": {}}

    mock_client._get.return_value = page1
    mock_client.get_absolute.side_effect = [page2, page3]

    people: List[int] = [p["id"] for p in people_api.iter_people({"limit": 1})]
    assert people == [1, 2, 3]

