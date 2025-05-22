"""
Core API client for interacting with the Follow Up Boss API.
"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional, IO
import logging

# Configure basic logging
# In a larger application, you might want to configure this in a central place.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv() # Load environment variables from .env file

class FollowUpBossApiException(Exception):
    """
    Custom exception for API-related errors.

    Attributes:
        status_code: HTTP status code of the error response.
        message: Error message from the API or a default message.
        response_data: The full JSON response data from the API, if available.
    """
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.response_data = response_data

    def __str__(self):
        return f"FollowUpBossApiException: [Status {self.status_code}] {self.message}"

class ApiClient:
    """
    A client for interacting with the Follow Up Boss API.
    Handles request authentication, construction, and error handling.
    """
    
    BASE_URL = "https://api.followupboss.com/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, x_system: Optional[str] = None, x_system_key: Optional[str] = None):
        """
        Initializes the API client.

        Args:
            api_key: The Follow Up Boss API key. If not provided, it will try to load
                     it from the FOLLOW_UP_BOSS_API_KEY environment variable.
            timeout: The timeout in seconds for requests.
            x_system: Optional X-System identifier for system-level integrations.
            x_system_key: Optional X-System-Key for system-level integrations.

        Raises:
            ValueError: If the API key is not provided and not found in environment variables.
        """
        self.api_key = api_key or os.getenv("FOLLOW_UP_BOSS_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as FOLLOW_UP_BOSS_API_KEY environment variable.")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (self.api_key, "") # Correct Basic Auth: API key as username, empty password
        self.session.headers.update({
            "accept": "application/json",
            # Authorization header is now handled by self.session.auth
        })
        # Add X-System headers if provided
        if x_system:
            self.session.headers["X-System"] = x_system
        if x_system_key:
            self.session.headers["X-System-Key"] = x_system_key

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None, 
        files: Optional[Dict[str, Any]] = None 
    ) -> Dict[str, Any]:
        """
        Internal method to make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint: API endpoint path (e.g., '/people').
            params: URL query parameters.
            json_data: Data to be sent as JSON in the request body.
            data: Data to be sent as form-data in the request body.
            files: Files to be uploaded (for multipart/form-data).

        Returns:
            The JSON response from the API as a dictionary.

        Raises:
            FollowUpBossApiException: If the API returns an error or the request fails.
        """
        url = f"{self.BASE_URL}{endpoint}"
        # Headers like Content-Type are generally handled by requests library based on `json`, `data`, or `files` params.
        # Session headers (accept, X-System, X-System-Key) are already set in self.session.headers.
        # The `current_headers` dictionary is for truly request-specific headers that override session headers,
        # or for headers like Content-Type that depend on the payload type.
        
        current_headers = {} # Start with empty dictionary for request-specific headers
        if json_data is not None and not files and not data:
            current_headers["Content-Type"] = "application/json"
        # For `data` (form-data) or `files` (multipart), requests sets Content-Type automatically.
        
        # Merge session headers with current_headers for the actual request
        # Giving precedence to current_headers if there are overlaps (e.g. Content-Type)
        final_headers = {**self.session.headers, **current_headers}

        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_data,
                data=data,
                files=files,
                timeout=self.timeout,
                headers=final_headers # Use the merged headers
            )
            response.raise_for_status()
            
            if response.status_code == 204:
                return {}
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            try:
                error_data = e.response.json()
                error_message = error_data.get("title", e.response.text) 
                if "errors" in error_data and isinstance(error_data["errors"], list) and error_data["errors"]:
                    error_details = [str(err.get("detail", err)) for err in error_data["errors"]]
                    error_message += ": " + ", ".join(error_details)
            except ValueError:
                error_data = None
                error_message = e.response.text
            raise FollowUpBossApiException(
                message=error_message,
                status_code=e.response.status_code,
                response_data=error_data
            ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception occurred: {e}")
            raise FollowUpBossApiException(message=str(e)) from e

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", endpoint, json_data=json_data, data=data, files=files)

    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("PUT", endpoint, json_data=json_data, data=data)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sends a DELETE request. Allows query parameters and JSON body."""
        return self._request("DELETE", endpoint, params=params, json_data=json_data)

"""
Potentially add other common methods like PATCH if needed by the API.
Example usage (outside this file, after importing):

if __name__ == '__main__':
    # This is for demonstration/testing within this file if run directly.
    # Ensure FOLLOW_UP_BOSS_API_KEY is in your .env file or passed directly.
    try:
        client = ApiClient()
        
        # Example: Get current user (Identity endpoint)
        # identity_info = client.get("/identity")
        # print("Identity Info:", identity_info)

        # Example: List a few people
        # people = client.get("/people", params={"limit": 2})
        # print("\nPeople:", people)

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except FollowUpBossApiException as e:
        print(f"API Error: {e.message}")
        if e.response_data:
            print(f"Response Data: {e.response_data}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

""" 