from typing import Any, Dict

import pytest

from follow_up_boss.people import People


@pytest.mark.unit
def test_list_people_passes_listid(mock_client: Any) -> None:
    people_api = People(mock_client)

    mock_client._get.return_value = {
        "people": [{"id": 1}],
        "_metadata": {"collection": "people"},
    }

    resp = people_api.list_people({"limit": 10, "listId": 154})
    assert resp["people"] == [{"id": 1}]
    # Validate call params
    mock_client._get.assert_called_once()
    called_params = mock_client._get.call_args.kwargs.get("params", {})
    assert called_params.get("listId") == 154
    assert called_params.get("limit") == 10


@pytest.mark.unit
def test_list_people_by_list_id_cursor(mock_client: Any) -> None:
    people_api = People(mock_client)

    page1: Dict[str, Any] = {
        "people": [{"id": 1}, {"id": 2}],
        "_metadata": {"collection": "people", "next": "TKN"},
    }
    page2: Dict[str, Any] = {
        "people": [{"id": 3}],
        "_metadata": {"collection": "people"},
    }

    def _fake_get(endpoint: str, params: Any = None) -> Dict[str, Any]:
        # Simulate cursor pagination by presence of "next"
        if params and "next" in params:
            return page2
        return page1

    mock_client._get.side_effect = _fake_get

    out = people_api.fetch_all_people_by_list_id(154, limit=2)
    assert [p["id"] for p in out] == [1, 2, 3]
