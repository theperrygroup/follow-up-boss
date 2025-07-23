"""
Enhanced API client for Follow Up Boss with session management and retry logic.

This module provides a robust API client that handles authentication timeouts,
implements retry logic, and manages connection pools for long-running operations.
"""

import logging
import os
import time
from functools import wraps
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .client import (
    API_KEY,
    BASE_URL,
    X_SYSTEM,
    X_SYSTEM_KEY,
    FollowUpBossApiClient,
    FollowUpBossApiException,
)

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)


class AuthenticationError(FollowUpBossApiException):
    """Raised when authentication fails or token expires."""

    pass


class MaxRetriesExceeded(FollowUpBossApiException):
    """Raised when maximum retry attempts are exceeded."""

    pass


def retry_on_auth_failure(max_retries: int = 3, backoff_factor: float = 1.0) -> Any:
    """
    Decorator to retry API calls on authentication failures.

    Args:
        max_retries: Maximum number of retry attempts.
        backoff_factor: Factor for exponential backoff between retries.
    """

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this is an authentication error
                    if self._is_auth_error(e):
                        if attempt < max_retries:
                            wait_time = backoff_factor * (2**attempt)
                            logger.warning(
                                f"Authentication error on attempt {attempt + 1}/{max_retries + 1}. "
                                f"Retrying in {wait_time} seconds..."
                            )
                            time.sleep(wait_time)

                            # Reinitialize session
                            self._reinitialize_session()
                            continue
                        else:
                            raise AuthenticationError(
                                f"Authentication failed after {max_retries} retries"
                            ) from e
                    else:
                        # Not an auth error, re-raise immediately
                        raise

            # If we get here, all retries failed
            raise MaxRetriesExceeded(
                f"Max retries ({max_retries}) exceeded"
            ) from last_exception

        return wrapper

    return decorator


class RobustApiClient(FollowUpBossApiClient):
    """
    Enhanced Follow Up Boss API client with robust error handling.

    Features:
    - Automatic retry on authentication failures
    - Session timeout recovery
    - Connection pooling
    - Rate limiting respect
    - Request logging and metrics
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        x_system: Optional[str] = None,
        x_system_key: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        timeout: int = 30,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ):
        """
        Initialize the robust API client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for the API.
            x_system: The X-System header value.
            x_system_key: The X-System-Key header value.
            max_retries: Maximum number of retry attempts.
            backoff_factor: Factor for exponential backoff.
            timeout: Request timeout in seconds.
            pool_connections: Number of connection pools.
            pool_maxsize: Maximum size of connection pool.
        """
        # Use default values from client.py if None provided
        # Initialize parent class
        super().__init__(
            api_key=api_key or API_KEY,
            base_url=base_url or BASE_URL,
            x_system=x_system or X_SYSTEM,
            x_system_key=x_system_key or X_SYSTEM_KEY,
        )

        # Retry configuration
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

        # Session management
        self.session: Optional[requests.Session] = None
        self.session_timeout_count = 0
        self.last_request_time: Optional[float] = None

        # Initialize session with connection pooling
        self._initialize_session(pool_connections, pool_maxsize)

        # Request tracking
        self.request_count = 0
        self.error_count = 0

    def _initialize_session(self, pool_connections: int, pool_maxsize: int) -> None:
        """
        Initialize requests session with connection pooling and retry strategy.

        Args:
            pool_connections: Number of connection pools.
            pool_maxsize: Maximum size of connection pool.
        """
        self.session = requests.Session()

        # Configure retry strategy for the session
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            respect_retry_after_header=True,
        )

        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy,
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info("Initialized robust API session with connection pooling")

    def _reinitialize_session(self) -> None:
        """Reinitialize session to handle timeouts and connection issues."""
        if self.session:
            self.session.close()

        self._initialize_session(10, 10)  # Default pool settings
        self.session_timeout_count += 1

        logger.info(
            f"Reinitialized session (timeout count: {self.session_timeout_count})"
        )

    def _is_auth_error(self, exception: Exception) -> bool:
        """
        Check if an exception is an authentication-related error.

        Args:
            exception: The exception to check.

        Returns:
            True if the exception is authentication-related.
        """
        error_str = str(exception).lower()
        auth_indicators = [
            "access token has expired",
            "unauthorized",
            "401",
            "authentication failed",
            "invalid token",
            "token expired",
        ]

        return any(indicator in error_str for indicator in auth_indicators)

    def _should_rate_limit(self) -> bool:
        """
        Check if we should rate limit the next request.

        Returns:
            True if we should wait before making the next request.
        """
        if self.last_request_time is None:
            return False

        # Implement basic rate limiting (max 10 requests per second)
        time_since_last = time.time() - self.last_request_time
        return time_since_last < 0.1  # 100ms between requests

    def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        if self._should_rate_limit() and self.last_request_time is not None:
            wait_time = 0.1 - (time.time() - self.last_request_time)
            if wait_time > 0:
                time.sleep(wait_time)

    @retry_on_auth_failure(max_retries=3, backoff_factor=1.0)
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Enhanced request method with retry logic and session management.

        Args:
            method: The HTTP method.
            endpoint: The API endpoint.
            params: URL parameters.
            data: Form data.
            json: JSON data.
            files: Files to upload.

        Returns:
            The API response.

        Raises:
            FollowUpBossApiException: If the request fails after retries.
        """
        # Rate limiting
        self._wait_for_rate_limit()

        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        auth = (self.api_key, "")

        # Remove Content-Type for file uploads
        if files:
            headers.pop("Content-Type", None)

        # Debug output
        logger.debug(f"Making {method} request to {url}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Headers: {headers}")

        try:
            self.request_count += 1
            start_time = time.time()

            if self.session is None:
                raise RuntimeError("Session not initialized")

            response = self.session.request(
                method,
                url,
                headers=headers,
                auth=auth,
                params=params,
                data=data,
                json=json,
                files=files,
                timeout=self.timeout,
            )

            self.last_request_time = time.time()
            request_duration = self.last_request_time - start_time

            logger.debug(f"Request completed in {request_duration:.2f}s")
            logger.debug(f"Response status: {response.status_code}")

            # Check for authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed (401 Unauthorized)")

            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as http_err:
            self.error_count += 1

            # Enhanced error handling
            error_message = f"HTTP error occurred: {http_err}"

            try:
                error_content = http_err.response.content.decode(
                    "utf-8", errors="replace"
                )
                logger.error(f"{error_message}")
                logger.error(f"Response content: {error_content}")

                # Try to parse JSON error response
                try:
                    error_data = http_err.response.json()
                    error_detail = error_data.get("title", error_content)

                    if "errors" in error_data and isinstance(
                        error_data["errors"], list
                    ):
                        details = [
                            str(err.get("detail", err)) for err in error_data["errors"]
                        ]
                        error_detail += ": " + ", ".join(details)

                    # Check for specific authentication errors
                    if "access token has expired" in error_detail.lower():
                        raise AuthenticationError(error_detail) from http_err

                    # Enhance error message with context
                    enhanced_error = self._enhance_error_message(
                        error_detail, endpoint, json
                    )

                    raise FollowUpBossApiException(
                        message=enhanced_error,
                        status_code=http_err.response.status_code,
                        response_data=error_data,
                    ) from http_err

                except ValueError:
                    # Not JSON, check for auth errors in plain text
                    if "access token has expired" in error_content.lower():
                        raise AuthenticationError(error_content) from http_err

                    enhanced_error = self._enhance_error_message(
                        error_content, endpoint, json
                    )
                    raise FollowUpBossApiException(
                        message=enhanced_error,
                        status_code=http_err.response.status_code,
                    ) from http_err

            except Exception as e:
                # Check if the original exception was an auth error
                if self._is_auth_error(http_err):
                    raise AuthenticationError(str(http_err)) from http_err

                # Fallback error handling
                status_code = getattr(http_err.response, "status_code", None)
                raise FollowUpBossApiException(
                    message=str(http_err),
                    status_code=status_code,
                ) from http_err

        except requests.exceptions.RequestException as req_err:
            self.error_count += 1
            logger.error(f"Request exception occurred: {req_err}")
            raise FollowUpBossApiException(message=str(req_err)) from req_err

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current session.

        Returns:
            Dictionary containing session statistics.
        """
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "session_timeout_count": self.session_timeout_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "last_request_time": self.last_request_time,
        }

    def close(self) -> None:
        """Close the session and clean up resources."""
        if self.session:
            self.session.close()
            logger.info("Closed API session")


class ConnectionManager:
    """
    Manages multiple API client connections for high-throughput operations.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        pool_size: int = 5,
        timeout_threshold: int = 300,
    ):
        """
        Initialize connection manager.

        Args:
            api_key: API key for all connections.
            pool_size: Number of client connections to maintain.
            timeout_threshold: Time threshold for connection rotation (seconds).
        """
        self.api_key = api_key
        self.pool_size = pool_size
        self.timeout_threshold = timeout_threshold
        self.clients = []
        self.current_client_index = 0

        # Initialize client pool
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the pool of API clients."""
        self.clients = []
        for i in range(self.pool_size):
            client = RobustApiClient(api_key=self.api_key)
            self.clients.append(client)

        logger.info(f"Initialized connection pool with {self.pool_size} clients")

    def get_client(self) -> RobustApiClient:
        """
        Get a fresh client from the pool.

        Returns:
            A robust API client instance.
        """
        # Rotate to the next client
        self.current_client_index = (self.current_client_index + 1) % self.pool_size
        return self.clients[self.current_client_index]

    def get_fresh_client(self) -> RobustApiClient:
        """
        Get a fresh client instance for long operations.

        Returns:
            A new robust API client instance.
        """
        return RobustApiClient(api_key=self.api_key)

    def close_all(self) -> None:
        """Close all client connections."""
        for client in self.clients:
            client.close()
        logger.info("Closed all connections in pool")
