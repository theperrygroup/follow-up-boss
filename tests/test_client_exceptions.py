from typing import Any, Dict, Optional

import pytest
import requests

from follow_up_boss.client import (
    FollowUpBossApiClient,
    FollowUpBossApiException,
    FollowUpBossAuthError,
    FollowUpBossNotFoundError,
    FollowUpBossRateLimitError,
    FollowUpBossServerError,
    FollowUpBossValidationError,
)


class FakeResponse:
    def __init__(self, status: int, body: Optional[Dict[str, Any]] = None) -> None:
        self.status_code = status
        self._body = body or {"title": "error"}
        self.headers: Dict[str, str] = {}
        self.text = "error"
        self.content = b"error"

    def json(self) -> Dict[str, Any]:
        return self._body

    def raise_for_status(self) -> None:
        http_err = requests.exceptions.HTTPError(f"{self.status_code} Client Error")
        http_err.response = self
        raise http_err


def _mock_request_returning(status: int) -> Any:
    def _call(*args: Any, **kwargs: Any) -> FakeResponse:
        return FakeResponse(status)

    return _call


@pytest.mark.parametrize(
    "status,exc",
    [
        (401, FollowUpBossAuthError),
        (403, FollowUpBossAuthError),
        (404, FollowUpBossNotFoundError),
        (429, FollowUpBossRateLimitError),
        (400, FollowUpBossValidationError),
        (500, FollowUpBossServerError),
    ],
)
def test_exception_mapping(monkeypatch: Any, status: int, exc: Any) -> None:
    client = FollowUpBossApiClient(api_key="x")
    monkeypatch.setattr(requests, "request", _mock_request_returning(status))

    with pytest.raises(exc):
        client._get("people")


def test_exception_default(monkeypatch: Any) -> None:
    client = FollowUpBossApiClient(api_key="x")
    # Use an uncommon status to hit the default mapping
    monkeypatch.setattr(requests, "request", _mock_request_returning(418))

    with pytest.raises(FollowUpBossApiException):
        client._get("people")
