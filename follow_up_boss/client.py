"""
API client for Follow Up Boss.
"""

import os
import re
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOLLOW_UP_BOSS_API_KEY")
BASE_URL = "https://api.followupboss.com/v1"
X_SYSTEM = os.getenv("X_SYSTEM")
X_SYSTEM_KEY = os.getenv("X_SYSTEM_KEY")


class FollowUpBossApiException(Exception):
    """
    Custom exception for API-related errors.

    Attributes:
        status_code: HTTP status code of the error response.
        message: Error message from the API or a default message.
        response_data: The full JSON response data from the API, if available.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        if self.status_code:
            return (
                f"FollowUpBossApiException: [Status {self.status_code}] {self.message}"
            )
        else:
            return f"FollowUpBossApiException: {self.message}"


class FollowUpBossApiClient:
    """
    A client for interacting with the Follow Up Boss API.

    Attributes:
        api_key: The API key for authentication.
        base_url: The base URL for the API.
        x_system: The X-System header value.
        x_system_key: The X-System-Key header value.
    """

    def __init__(
        self,
        api_key: Optional[str] = API_KEY,
        base_url: str = BASE_URL,
        x_system: Optional[str] = X_SYSTEM,
        x_system_key: Optional[str] = X_SYSTEM_KEY,
    ) -> None:
        """
        Initializes the FollowUpBossApiClient.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for the API.
            x_system: The X-System header value.
            x_system_key: The X-System-Key header value.

        Raises:
            ValueError: If the API key is not provided.
        """
        if not api_key:
            raise ValueError(
                "API key not found. Please set FOLLOW_UP_BOSS_API_KEY in your .env file or pass it to the client."
            )
        self.api_key = api_key
        self.base_url = base_url
        self.x_system = x_system
        self.x_system_key = x_system_key

    def _get_headers(self) -> Dict[str, str]:
        """
        Returns the headers for API requests.
        Does not include Authorization, as that's handled by `auth` in _request.

        Returns:
            A dictionary of headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Add system headers only if they exist
        if self.x_system is not None:
            headers["X-System"] = self.x_system
        if self.x_system_key is not None:
            headers["X-System-Key"] = self.x_system_key

        return headers

    def _enhance_error_message(
        self,
        error_message: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Enhance error messages with context-specific guidance.

        Args:
            error_message: The original error message.
            endpoint: The API endpoint being called.
            json_data: The JSON data that was sent in the request.

        Returns:
            Enhanced error message with helpful guidance.
        """
        enhanced_message = error_message

        # Deal-specific error enhancements
        if "deals" in endpoint and json_data:
            # Check for commission field related errors
            if any(
                field in str(json_data)
                for field in ["commissionValue", "agentCommission", "teamCommission"]
            ):
                if (
                    "invalid" in error_message.lower()
                    or "field" in error_message.lower()
                ):
                    enhanced_message += (
                        "\n\nDEAL COMMISSION GUIDANCE:\n"
                        "Commission fields (commissionValue, agentCommission, teamCommission) must be passed as "
                        "top-level parameters when creating/updating deals, not in custom_fields.\n"
                        "Example: create_deal(name='Deal', stage_id=1, commissionValue=13500.0)"
                    )

            # Check for required field errors
            if "required" in error_message.lower() and "stage" in error_message.lower():
                enhanced_message += (
                    "\n\nDEAL CREATION GUIDANCE:\n"
                    "The 'stage_id' parameter is required for all deal creation. "
                    "Get valid stage IDs from the stages API endpoint."
                )

        # Field name guidance
        if (
            "invalid field" in error_message.lower()
            or "unknown field" in error_message.lower()
        ):
            enhanced_message += (
                "\n\nFIELD NAME GUIDANCE:\n"
                "The API expects camelCase field names. Common mappings:\n"
                "- close_date → projectedCloseDate\n"
                "- user_id → userId\n"
                "- person_id → personId\n"
                "- stage_id → stageId\n"
                "- pipeline_id → pipelineId"
            )

        return enhanced_message

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
        Makes a request to the Follow Up Boss API.

        Args:
            method: The HTTP method (GET, POST, PUT, DELETE).
            endpoint: The API endpoint.
            params: URL parameters for the request.
            data: Form data for the request body.
            json: JSON data for the request body.
            files: Files to upload.

        Returns:
            The response from the API.

        Raises:
            FollowUpBossApiException: If the API returns an error or the request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        auth = (self.api_key, "")  # API Key as username, empty password

        # If we have files, we should not set Content-Type, let requests set it with the boundary
        if files:
            headers.pop("Content-Type", None)

        # Debug output for request
        print(f"\n=== API Request ===")
        print(f"Method: {method}")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        print(f"JSON: {json}")
        print(f"Data: {data}")
        print(f"Files: {files}")

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                auth=auth,  # Use Basic Auth
                params=params,
                data=data,
                json=json,
                files=files,
                timeout=30,  # Adding a timeout for requests
            )

            # Debug output for response
            print(f"\n=== API Response ===")
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            try:
                print(f"Response JSON: {response.json()}")
            except Exception:
                print(f"Response Text: {response.text}")

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}"
            try:
                error_content = http_err.response.content.decode(
                    "utf-8", errors="replace"
                )
                print(f"{error_message}")
                print(f"Response content: {error_content}")

                # Try to parse JSON error response if available
                try:
                    error_data = http_err.response.json()
                    error_detail = error_data.get("title", error_content)
                    if (
                        "errors" in error_data
                        and isinstance(error_data["errors"], list)
                        and error_data["errors"]
                    ):
                        details = [
                            str(err.get("detail", err)) for err in error_data["errors"]
                        ]
                        error_detail += ": " + ", ".join(details)

                    # Enhance the error message with context-specific guidance
                    enhanced_error = self._enhance_error_message(
                        error_detail, endpoint, json
                    )

                    raise FollowUpBossApiException(
                        message=enhanced_error,
                        status_code=http_err.response.status_code,
                        response_data=error_data,
                    ) from http_err
                except ValueError:
                    # If not JSON, just use the content as error message
                    enhanced_error = self._enhance_error_message(
                        error_content, endpoint, json
                    )
                    raise FollowUpBossApiException(
                        message=enhanced_error,
                        status_code=http_err.response.status_code,
                    ) from http_err
            except Exception:
                # Fallback to original error if we can't parse response
                status_code = None
                # Try to extract status code from error message (e.g., "404 Client Error")
                error_str = str(http_err)
                if error_str.startswith(("4", "5")) and " " in error_str:
                    try:
                        status_code = int(error_str.split(" ")[0])
                    except (ValueError, IndexError):
                        pass
                raise FollowUpBossApiException(
                    message=str(http_err), status_code=status_code
                ) from http_err
        except requests.exceptions.RequestException as req_err:
            print(f"Request exception occurred: {req_err}")
            raise FollowUpBossApiException(message=str(req_err)) from req_err

    def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Helper method for GET requests."""
        response = self._request("GET", endpoint, params=params)
        json_response = response.json()
        return json_response if isinstance(json_response, dict) else {}

    def _post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], str]:
        """Helper method for POST requests."""
        response = self._request(
            "POST", endpoint, params=params, data=data, json=json_data, files=files
        )
        try:
            json_response = response.json()
            return json_response if isinstance(json_response, dict) else {}
        except requests.exceptions.JSONDecodeError:
            # Handle cases where response might not be JSON (e.g., 204 No Content)
            return response.text

    def _put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], str]:
        """Helper method for PUT requests."""
        response = self._request(
            "PUT", endpoint, data=data, json=json_data, files=files
        )
        try:
            json_response = response.json()
            return json_response if isinstance(json_response, dict) else {}
        except requests.exceptions.JSONDecodeError:
            return response.text

    def _delete(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], str]:
        """Helper method for DELETE requests."""
        response = self._request("DELETE", endpoint, data=data, json=json_data)
        # DELETE often returns 204 No Content, which is not valid JSON
        if response.status_code == 204:
            return ""
        try:
            json_response = response.json()
            return json_response if isinstance(json_response, dict) else {}
        except requests.exceptions.JSONDecodeError:
            return response.text
