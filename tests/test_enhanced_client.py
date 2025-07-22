"""
Tests for enhanced client functionality including RobustApiClient, 
authentication handling, retry logic, and session management.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from follow_up_boss.client import FollowUpBossApiException
from follow_up_boss.enhanced_client import (
    AuthenticationError,
    ConnectionManager,
    MaxRetriesExceeded,
    RobustApiClient,
    retry_on_auth_failure,
)


@pytest.mark.unit
class TestRobustApiClient:
    """Test cases for RobustApiClient functionality."""

    def test_initialization_with_defaults(self):
        """Test RobustApiClient initialization with default parameters."""
        client = RobustApiClient(api_key="test_key")

        assert client.api_key == "test_key"
        assert client.max_retries == 3
        assert client.backoff_factor == 1.0
        assert client.timeout == 30
        assert client.request_count == 0
        assert client.error_count == 0
        assert client.session_timeout_count == 0

    def test_initialization_with_custom_params(self):
        """Test RobustApiClient initialization with custom parameters."""
        client = RobustApiClient(
            api_key="test_key",
            max_retries=5,
            backoff_factor=2.0,
            timeout=60,
            pool_connections=20,
            pool_maxsize=30,
        )

        assert client.max_retries == 5
        assert client.backoff_factor == 2.0
        assert client.timeout == 60

    def test_session_initialization(self):
        """Test that session is properly initialized."""
        client = RobustApiClient(api_key="test_key")

        assert client.session is not None
        assert hasattr(client.session, "mount")
        assert hasattr(client.session, "request")

    def test_is_auth_error_detection(self):
        """Test authentication error detection."""
        client = RobustApiClient(api_key="test_key")

        # Test various authentication error messages
        auth_errors = [
            Exception("Access token has expired"),
            Exception("401 Unauthorized"),
            Exception("Authentication failed"),
            Exception("Invalid token"),
            Exception("Token expired"),
        ]

        for error in auth_errors:
            assert client._is_auth_error(error) is True

        # Test non-auth errors
        non_auth_errors = [
            Exception("Network timeout"),
            Exception("404 Not Found"),
            Exception("Internal server error"),
        ]

        for error in non_auth_errors:
            assert client._is_auth_error(error) is False

    def test_rate_limiting_logic(self):
        """Test rate limiting functionality."""
        client = RobustApiClient(api_key="test_key")

        # First request - no rate limiting
        assert client._should_rate_limit() is False

        # Set last request time to recent
        client.last_request_time = time.time()

        # Second request immediately - should rate limit
        assert client._should_rate_limit() is True

        # Set last request time to past
        client.last_request_time = time.time() - 1.0

        # Request after sufficient time - no rate limiting
        assert client._should_rate_limit() is False

    @patch("time.sleep")
    def test_wait_for_rate_limit(self, mock_sleep):
        """Test rate limit waiting functionality."""
        client = RobustApiClient(api_key="test_key")

        # Set recent request time
        client.last_request_time = time.time() - 0.05  # 50ms ago

        client._wait_for_rate_limit()

        # Should have called sleep with remaining wait time
        mock_sleep.assert_called_once()
        call_args = mock_sleep.call_args[0][0]
        assert 0 < call_args < 0.1  # Should be less than 100ms

    def test_session_stats(self):
        """Test session statistics tracking."""
        client = RobustApiClient(api_key="test_key")

        # Initial stats
        stats = client.get_session_stats()
        assert stats["request_count"] == 0
        assert stats["error_count"] == 0
        assert stats["session_timeout_count"] == 0
        assert stats["error_rate"] == 0.0
        assert stats["last_request_time"] is None

        # Update stats manually for testing
        client.request_count = 10
        client.error_count = 2
        client.session_timeout_count = 1
        client.last_request_time = 1640995200.0

        stats = client.get_session_stats()
        assert stats["request_count"] == 10
        assert stats["error_count"] == 2
        assert stats["session_timeout_count"] == 1
        assert stats["error_rate"] == 0.2
        assert stats["last_request_time"] == 1640995200.0

    def test_session_reinitialization(self):
        """Test session reinitialization functionality."""
        client = RobustApiClient(api_key="test_key")

        original_session = client.session
        original_timeout_count = client.session_timeout_count

        client._reinitialize_session()

        # Session should be different and timeout count incremented
        assert client.session is not original_session
        assert client.session_timeout_count == original_timeout_count + 1

    def test_close_session(self):
        """Test session closing functionality."""
        client = RobustApiClient(api_key="test_key")

        mock_session = Mock()
        client.session = mock_session

        client.close()

        mock_session.close.assert_called_once()


@pytest.mark.unit
class TestAuthenticationHandling:
    """Test cases for authentication and retry logic."""

    @patch("time.sleep")
    def test_retry_decorator_with_auth_error(self, mock_sleep):
        """Test retry decorator with authentication errors."""

        class TestClient:
            def __init__(self):
                self.call_count = 0
                self.session_reinit_count = 0

            def _is_auth_error(self, error):
                return "auth" in str(error).lower()

            def _reinitialize_session(self):
                self.session_reinit_count += 1

            @retry_on_auth_failure(max_retries=2, backoff_factor=1.0)
            def test_method(self):
                self.call_count += 1
                if self.call_count < 3:
                    raise Exception("Auth error")
                return "success"

        client = TestClient()
        result = client.test_method()

        assert result == "success"
        assert client.call_count == 3
        assert client.session_reinit_count == 2
        assert mock_sleep.call_count == 2

    def test_retry_decorator_with_non_auth_error(self):
        """Test retry decorator with non-authentication errors."""

        class TestClient:
            def __init__(self):
                self.call_count = 0

            def _is_auth_error(self, error):
                return False

            def _reinitialize_session(self):
                pass

            @retry_on_auth_failure(max_retries=2)
            def test_method(self):
                self.call_count += 1
                raise Exception("Network error")

        client = TestClient()

        with pytest.raises(Exception, match="Network error"):
            client.test_method()

        # Should not retry for non-auth errors
        assert client.call_count == 1

    def test_retry_decorator_max_retries_exceeded(self):
        """Test retry decorator when max retries are exceeded."""

        class TestClient:
            def __init__(self):
                self.call_count = 0

            def _is_auth_error(self, error):
                return True

            def _reinitialize_session(self):
                pass

            @retry_on_auth_failure(max_retries=2)
            def test_method(self):
                self.call_count += 1
                raise Exception("Auth error")

        client = TestClient()

        with pytest.raises(
            AuthenticationError, match="Authentication failed after 2 retries"
        ):
            client.test_method()

        assert client.call_count == 3  # Initial call + 2 retries


@pytest.mark.unit
class TestConnectionManager:
    """Test cases for ConnectionManager functionality."""

    def test_initialization(self):
        """Test ConnectionManager initialization."""
        manager = ConnectionManager(api_key="test_key", pool_size=3)

        assert manager.api_key == "test_key"
        assert manager.pool_size == 3
        assert len(manager.clients) == 3
        assert manager.current_client_index == 0

    def test_get_client_rotation(self):
        """Test client rotation in connection pool."""
        manager = ConnectionManager(api_key="test_key", pool_size=3)

        # Get clients and verify rotation
        client1 = manager.get_client()
        assert manager.current_client_index == 1

        client2 = manager.get_client()
        assert manager.current_client_index == 2

        client3 = manager.get_client()
        assert manager.current_client_index == 0  # Should wrap around

        # Verify clients are different instances
        assert client1 is not client2
        assert client2 is not client3
        assert client3 is not client1

    def test_get_fresh_client(self):
        """Test getting a fresh client instance."""
        manager = ConnectionManager(api_key="test_key", pool_size=2)

        fresh_client = manager.get_fresh_client()
        pooled_client = manager.get_client()

        # Fresh client should not be in the pool
        assert fresh_client not in manager.clients
        assert fresh_client is not pooled_client

    def test_close_all_clients(self):
        """Test closing all clients in the pool."""
        manager = ConnectionManager(api_key="test_key", pool_size=2)

        # Mock the close method for all clients
        for client in manager.clients:
            client.close = Mock()

        manager.close_all()

        # Verify all clients were closed
        for client in manager.clients:
            client.close.assert_called_once()


@pytest.mark.integration
class TestRobustApiClientIntegration:
    """Integration tests for RobustApiClient with real API calls."""

    def test_successful_request(self, robust_client):
        """Test successful API request with RobustApiClient."""
        response = robust_client._get("identity")

        assert isinstance(response, dict)
        assert robust_client.request_count >= 1
        assert robust_client.error_count == 0

    def test_invalid_endpoint_error_handling(self, robust_client):
        """Test error handling for invalid endpoints."""
        with pytest.raises(FollowUpBossApiException):
            robust_client._get("invalid_endpoint_12345")

        assert robust_client.error_count >= 1

    @pytest.mark.slow
    def test_rate_limiting_in_practice(self, robust_client):
        """Test rate limiting with multiple rapid requests."""
        start_time = time.time()

        # Make multiple rapid requests
        for i in range(5):
            robust_client._get("identity")

        end_time = time.time()
        elapsed = end_time - start_time

        # Should take at least some time due to rate limiting
        assert elapsed >= 0.4  # At least 400ms for 5 requests with 100ms spacing
        assert robust_client.request_count >= 5


@pytest.mark.unit
class TestErrorScenarios:
    """Test various error scenarios and edge cases."""

    @patch("requests.Session")
    def test_session_request_failure(self, mock_session_class):
        """Test handling of session request failures."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.request.side_effect = ConnectionError("Network error")

        client = RobustApiClient(api_key="test_key")

        with pytest.raises(FollowUpBossApiException, match="Network error"):
            client._request("GET", "test_endpoint")

        assert client.error_count == 1

    @patch("requests.Session")
    def test_http_error_handling(self, mock_session_class):
        """Test handling of HTTP errors."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = HTTPError("Server error")
        mock_response.content = b'{"error": "Internal server error"}'
        mock_response.json.return_value = {"error": "Internal server error"}

        mock_session.request.return_value = mock_response

        client = RobustApiClient(api_key="test_key")

        with pytest.raises(FollowUpBossApiException):
            client._request("GET", "test_endpoint")

        assert client.error_count == 1

    def test_missing_api_key_error(self):
        """Test error handling for missing API key."""
        with pytest.raises(ValueError, match="API key not found"):
            RobustApiClient(api_key=None)

    def test_authentication_error_detection_in_request(self):
        """Test authentication error detection in actual requests."""
        client = RobustApiClient(api_key="test_key")

        # Mock an authentication error response
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Authentication failed"):
                client._request("GET", "test_endpoint")


@pytest.mark.unit
class TestEnhancedFeatures:
    """Test enhanced features specific to RobustApiClient."""

    def test_request_tracking(self):
        """Test request and error tracking."""
        client = RobustApiClient(api_key="test_key")

        assert client.request_count == 0
        assert client.error_count == 0

        # Mock successful request
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response

            client._request("GET", "test_endpoint")

            assert client.request_count == 1
            assert client.error_count == 0

        # Mock failed request
        with patch.object(client.session, "request") as mock_request:
            mock_request.side_effect = ConnectionError("Network error")

            with pytest.raises(FollowUpBossApiException):
                client._request("GET", "test_endpoint")

            assert client.request_count == 2
            assert client.error_count == 1

    def test_session_timeout_tracking(self):
        """Test session timeout tracking."""
        client = RobustApiClient(api_key="test_key")

        initial_count = client.session_timeout_count

        client._reinitialize_session()

        assert client.session_timeout_count == initial_count + 1

    def test_last_request_time_tracking(self):
        """Test last request time tracking."""
        client = RobustApiClient(api_key="test_key")

        assert client.last_request_time is None

        # Mock successful request
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response

            before_time = time.time()
            client._request("GET", "test_endpoint")
            after_time = time.time()

            assert client.last_request_time is not None
            assert before_time <= client.last_request_time <= after_time
