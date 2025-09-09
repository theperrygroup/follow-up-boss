"""
Unit tests for listing people by Smart List ID with cursor pagination.
"""

from typing import Any, Dict, List

import pytest

from follow_up_boss.people import People


@pytest.mark.unit
def test_list_people_by_list_id_single_page(mock_client: Any) -> None:
    """Verify a single-page fetch with listId and limit passes correct params and returns data."""
    people_api = People(mock_client)

    payload: Dict[str, Any] = {
        "_metadata": {"collection": "people", "limit": 10, "offset": 0},
        "people": [{"id": 1}, {"id": 2}],
    }

    mock_client._get.return_value = payload

    data = people_api.list_people_by_list_id(154, limit=10)

    assert data == payload
    mock_client._get.assert_called_once_with(
        "people", params={"listId": 154, "limit": 10}
    )


@pytest.mark.unit
def test_list_people_by_list_id_with_next_token(mock_client: Any) -> None:
    """Verify next token is forwarded as the 'next' query parameter."""
    people_api = People(mock_client)

    payload: Dict[str, Any] = {
        "_metadata": {"collection": "people", "limit": 10, "next": "TOKEN123"},
        "people": [{"id": 1}],
    }

    mock_client._get.return_value = payload

    data = people_api.list_people_by_list_id(154, limit=10, next_token="TOKEN123")

    assert data == payload
    mock_client._get.assert_called_once_with(
        "people", params={"listId": 154, "limit": 10, "next": "TOKEN123"}
    )


@pytest.mark.unit
def test_list_people_by_list_id_invalid_list_id(mock_client: Any) -> None:
    """Ensure invalid list_id raises ValueError."""
    people_api = People(mock_client)

    with pytest.raises(ValueError):
        people_api.list_people_by_list_id(0)

    with pytest.raises(ValueError):
        people_api.list_people_by_list_id(-5)


@pytest.mark.unit
def test_fetch_all_people_by_list_id_cursor_pagination(mock_client: Any) -> None:
    """Verify the pagination helper aggregates results across pages using _metadata.next."""
    people_api = People(mock_client)

    page1: Dict[str, Any] = {
        "_metadata": {"collection": "people", "limit": 2, "next": "TOKEN123"},
        "people": [{"id": 1}, {"id": 2}],
    }
    page2: Dict[str, Any] = {
        "_metadata": {"collection": "people", "limit": 2},
        "people": [{"id": 3}],
    }

    mock_client._get.side_effect = [page1, page2]

    all_people: List[Dict[str, Any]] = people_api.fetch_all_people_by_list_id(
        154, limit=2
    )
    assert [p["id"] for p in all_people] == [1, 2, 3]

    # Two calls: first without next, second with next token
    assert mock_client._get.call_count == 2
    first_call = mock_client._get.call_args_list[0]
    second_call = mock_client._get.call_args_list[1]
    assert first_call.kwargs["params"] == {"listId": 154, "limit": 2}
    assert second_call.kwargs["params"] == {
        "listId": 154,
        "limit": 2,
        "next": "TOKEN123",
    }
