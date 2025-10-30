from typing import Any, Dict, Optional

import pytest

from follow_up_boss.client import FollowUpBossApiClient


class DummyResponse:
    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        self.headers = headers or {}


@pytest.mark.unit
def test_extract_pagination_links() -> None:
    client = FollowUpBossApiClient(api_key="x")
    link_header = (
        '<https://api.followupboss.com/v1/people?next=T1>; rel="next", '
        '<https://api.followupboss.com/v1/people?prev=P1>; rel="prev"'
    )
    resp = DummyResponse({"Link": link_header})

    links = client._extract_pagination_links(resp)  # type: ignore[arg-type]
    assert links is not None
    assert links.get("nextLink", "").endswith("next=T1")
    assert links.get("prevLink", "").endswith("prev=P1")


@pytest.mark.unit
def test_extract_rate_limit_info() -> None:
    client = FollowUpBossApiClient(api_key="x")
    resp = DummyResponse(
        {
            "X-RateLimit-Limit": "120",
            "X-RateLimit-Remaining": "118",
            "X-RateLimit-Reset": "1710000000",
        }
    )

    info = client._extract_rate_limit_info(resp)  # type: ignore[arg-type]
    assert info == {"limit": 120, "remaining": 118, "reset": 1710000000}


@pytest.mark.unit
def test_get_absolute_calls_get(monkeypatch: Any) -> None:
    called: Dict[str, Any] = {}
    client = FollowUpBossApiClient(api_key="x")

    def fake_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        called["endpoint"] = endpoint
        called["params"] = params
        return {"ok": True}

    # monkeypatch the instance method
    monkeypatch.setattr(client, "_get", fake_get)

    out = client.get_absolute("https://api.followupboss.com/v1/people?next=T1")
    assert out == {"ok": True}
    assert str(called.get("endpoint", "")).startswith("https://api.followupboss.com/")

