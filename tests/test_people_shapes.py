from typing import Any, Dict, Optional

import pytest

from follow_up_boss.people import People


@pytest.mark.unit
def test_list_people_consistent_shape_without_metadata(mock_client: Any) -> None:
    people_api = People(mock_client)

    mock_client._get.return_value = {"people": [{"id": 1}, {"id": 2}]}

    resp = people_api.list_people({"limit": 2})
    assert "people" in resp
    assert resp.get("count") == 2
    # _metadata is optional but should be present as an empty dict or enriched
    assert isinstance(resp.get("_metadata", {}), dict)


@pytest.mark.unit
def test_iter_people_offset_fallback(mock_client: Any) -> None:
    people_api = People(mock_client)

    # Simulate offset-based pages (no nextLink and no next cursor)
    page1 = {"people": [{"id": 1}, {"id": 2}], "_metadata": {}}
    page2 = {"people": [{"id": 3}], "_metadata": {}}

    # _get is called by list_people; return different pages based on provided offset
    def _fake_get(
        endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        offset = (params or {}).get("offset", 0)
        if offset == 0:
            return page1
        return page2

    mock_client._get.side_effect = _fake_get

    out_ids = [p["id"] for p in people_api.iter_people({"limit": 2, "offset": 0})]
    assert out_ids == [1, 2, 3]
