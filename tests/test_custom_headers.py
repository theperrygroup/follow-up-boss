"""
Test the custom headers functionality in FollowUpBossApiClient.
"""

import os
from unittest.mock import Mock, patch

import pytest
import requests

from follow_up_boss.client import FollowUpBossApiClient


class TestCustomHeaders:
    """Test custom headers functionality."""

    def test_client_initialization_with_custom_headers(self) -> None:
        """Test that the client can be initialized with custom headers."""
        custom_headers = {
            "X-System": "MyTestSystem",
            "User-Agent": "My Custom User Agent",
            "X-Custom": "custom-value",
        }

        client = FollowUpBossApiClient(
            api_key="test_key", custom_headers=custom_headers
        )

        assert client.custom_headers == custom_headers

    def test_client_initialization_without_custom_headers(self) -> None:
        """Test that the client works without custom headers (backward compatibility)."""
        client = FollowUpBossApiClient(api_key="test_key")

        assert client.custom_headers == {}

    def test_client_initialization_with_none_custom_headers(self) -> None:
        """Test that the client handles None custom headers properly."""
        client = FollowUpBossApiClient(api_key="test_key", custom_headers=None)

        assert client.custom_headers == {}

    def test_get_headers_with_custom_headers(self) -> None:
        """Test that _get_headers includes custom headers."""
        custom_headers = {
            "X-System": "MyTestSystem",
            "User-Agent": "My Custom User Agent",
            "X-Custom": "custom-value",
        }

        client = FollowUpBossApiClient(
            api_key="test_key", custom_headers=custom_headers
        )

        headers = client._get_headers()

        # Check that default headers are present
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

        # Check that custom headers are present
        assert headers["X-System"] == "MyTestSystem"
        assert headers["User-Agent"] == "My Custom User Agent"
        assert headers["X-Custom"] == "custom-value"

    def test_get_headers_custom_override_defaults(self) -> None:
        """Test that custom headers override default headers."""
        custom_headers = {
            "Content-Type": "application/xml",  # Override default
            "Accept": "text/plain",  # Override default
            "X-Custom": "custom-value",
        }

        client = FollowUpBossApiClient(
            api_key="test_key", custom_headers=custom_headers
        )

        headers = client._get_headers()

        # Check that custom headers override defaults
        assert headers["Content-Type"] == "application/xml"
        assert headers["Accept"] == "text/plain"
        assert headers["X-Custom"] == "custom-value"

    def test_get_headers_protected_headers_filtered(self) -> None:
        """Test that protected headers are filtered out."""
        custom_headers = {
            "Authorization": "Bearer malicious-token",  # Should be filtered
            "Content-Length": "123",  # Should be filtered
            "X-Custom": "custom-value",  # Should be included
        }

        client = FollowUpBossApiClient(
            api_key="test_key", custom_headers=custom_headers
        )

        headers = client._get_headers()

        # Check that protected headers are not included
        assert "Authorization" not in headers
        assert "Content-Length" not in headers

        # Check that safe custom headers are included
        assert headers["X-Custom"] == "custom-value"

    def test_get_headers_case_insensitive_protection(self) -> None:
        """Test that protected headers are filtered case-insensitively."""
        custom_headers = {
            "AUTHORIZATION": "Bearer malicious-token",  # Should be filtered
            "content-length": "123",  # Should be filtered
            "Content-LENGTH": "456",  # Should be filtered
            "X-Custom": "custom-value",  # Should be included
        }

        client = FollowUpBossApiClient(
            api_key="test_key", custom_headers=custom_headers
        )

        headers = client._get_headers()

        # Check that protected headers are not included (case insensitive)
        assert "AUTHORIZATION" not in headers
        assert "content-length" not in headers
        assert "Content-LENGTH" not in headers

        # Check that safe custom headers are included
        assert headers["X-Custom"] == "custom-value"

    def test_backward_compatibility_with_legacy_system_headers(self) -> None:
        """Test that legacy x_system and x_system_key parameters still work."""
        client = FollowUpBossApiClient(
            api_key="test_key", x_system="LegacySystem", x_system_key="legacy-key"
        )

        headers = client._get_headers()

        # Check that legacy system headers are present
        assert headers["X-System"] == "LegacySystem"
        assert headers["X-System-Key"] == "legacy-key"

    def test_custom_headers_override_legacy_system_headers(self) -> None:
        """Test that custom headers override legacy system headers."""
        custom_headers = {"X-System": "NewSystem", "X-System-Key": "new-key"}

        client = FollowUpBossApiClient(
            api_key="test_key",
            x_system="LegacySystem",
            x_system_key="legacy-key",
            custom_headers=custom_headers,
        )

        headers = client._get_headers()

        # Check that custom headers override legacy headers
        assert headers["X-System"] == "NewSystem"
        assert headers["X-System-Key"] == "new-key"

    @patch("requests.request")
    def test_request_includes_custom_headers(self, mock_request: Mock) -> None:
        """Test that actual requests include custom headers."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        mock_response.headers = {}  # Fix the mock headers issue
        mock_request.return_value = mock_response

        custom_headers = {"X-System": "TestSystem", "User-Agent": "Custom User Agent"}

        client = FollowUpBossApiClient(
            api_key="test_key", custom_headers=custom_headers
        )

        # Make a request
        client._get("test_endpoint")

        # Verify the request was called with custom headers
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]

        assert "headers" in call_kwargs
        headers = call_kwargs["headers"]

        # Check that custom headers are included
        assert headers["X-System"] == "TestSystem"
        assert headers["User-Agent"] == "Custom User Agent"

        # Check that default headers are still present
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


@pytest.mark.integration
class TestCustomHeadersIntegration:
    """Integration tests for custom headers functionality."""

    def test_real_api_request_with_custom_headers(self) -> None:
        """Test making a real API request with custom headers."""
        api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
        if not api_key:
            pytest.skip("FOLLOW_UP_BOSS_API_KEY not set")

        custom_headers = {
            "X-System": "PythonLibraryTestSuite",
            "User-Agent": "FollowUpBoss-Python-Library/Test",
        }

        client = FollowUpBossApiClient(api_key=api_key, custom_headers=custom_headers)

        # Test with identity endpoint (simple and safe)
        from follow_up_boss.identity import Identity

        identity = Identity(client)

        # This should work with custom headers
        response = identity.get_identity()

        # Verify we got a valid response
        assert isinstance(response, dict)
        assert "account" in response
        assert "user" in response

    def test_x_system_header_for_rate_limiting(self) -> None:
        """Test that X-System header is properly sent for rate limiting benefits."""
        api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
        x_system = os.getenv("X_SYSTEM")
        x_system_key = os.getenv("X_SYSTEM_KEY")

        if not all([api_key, x_system, x_system_key]):
            pytest.skip("Required environment variables not set")

        # Test with custom headers approach
        # We know these are not None due to the check above
        assert x_system is not None
        assert x_system_key is not None
        custom_headers = {"X-System": x_system, "X-System-Key": x_system_key}

        client = FollowUpBossApiClient(api_key=api_key, custom_headers=custom_headers)

        # Test with identity endpoint
        from follow_up_boss.identity import Identity

        identity = Identity(client)

        # This should work with system registration headers
        response = identity.get_identity()

        # Verify we got a valid response
        assert isinstance(response, dict)
        assert "account" in response
        assert "user" in response


class TestCustomHeadersDocumentationExamples:
    """Test the usage examples from the documentation."""

    def test_basic_usage_example(self) -> None:
        """Test the basic usage example from the feature request."""
        # Basic usage (existing functionality preserved)
        client = FollowUpBossApiClient(api_key="your_api_key")

        assert client.custom_headers == {}
        assert client.api_key == "your_api_key"

    def test_enhanced_usage_example(self) -> None:
        """Test the enhanced usage example from the feature request."""
        # Enhanced usage with X-System header
        client = FollowUpBossApiClient(
            api_key="your_api_key", custom_headers={"X-System": "YourSystemName"}
        )

        assert client.custom_headers == {"X-System": "YourSystemName"}
        assert client.api_key == "your_api_key"

        # Verify headers are correctly set
        headers = client._get_headers()
        assert headers["X-System"] == "YourSystemName"

    @patch("requests.request")
    def test_usage_with_people_api(self, mock_request: Mock) -> None:
        """Test usage example with People API."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "name": "Test Person"}
        mock_response.raise_for_status = Mock()
        mock_response.headers = {}  # Fix the mock headers issue
        mock_request.return_value = mock_response

        # Enhanced usage with X-System header
        client = FollowUpBossApiClient(
            api_key="your_api_key", custom_headers={"X-System": "YourSystemName"}
        )

        # Use with People API
        from follow_up_boss.people import People

        people = People(client)

        person_data = {
            "name": "Test Person",
            "emails": [{"value": "test@example.com", "type": "work"}],
        }

        result = people.create_person(person_data)

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == 123
        assert result["name"] == "Test Person"

        # Verify the request was made with custom headers
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        headers = call_kwargs["headers"]
        assert headers["X-System"] == "YourSystemName"


if __name__ == "__main__":
    pytest.main([__file__])
