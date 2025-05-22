'''
API client for Follow Up Boss.
'''

import os
import requests
from dotenv import load_dotenv
from typing import Any, Dict, Optional, Union

load_dotenv()

API_KEY = os.getenv("FOLLOW_UP_BOSS_API_KEY")
BASE_URL = "https://api.followupboss.com/v1"
X_SYSTEM = os.getenv("X_SYSTEM")
X_SYSTEM_KEY = os.getenv("X_SYSTEM_KEY")

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
        x_system: Optional[str]= X_SYSTEM,
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
            raise ValueError("API key not found. Please set FOLLOW_UP_BOSS_API_KEY in your .env file or pass it to the client.")
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
        return {
            # "Authorization": f"Basic {self.api_key}", # This is handled by auth param
            "X-System": self.x_system,
            "X-System-Key": self.x_system_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Makes a request to the Follow Up Boss API.

        Args:
            method: The HTTP method (GET, POST, PUT, DELETE).
            endpoint: The API endpoint.
            params: URL parameters for the request.
            data: Form data for the request body.
            json: JSON data for the request body.

        Returns:
            The response from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        auth = (self.api_key, "") # API Key as username, empty password

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                auth=auth, # Use Basic Auth
                params=params,
                data=data,
                json=json,
                timeout=30  # Adding a timeout for requests
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {http_err.response.content.decode('utf-8', errors='replace')}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Request exception occurred: {req_err}")
            raise
            
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Helper method for GET requests."""
        response = self._request("GET", endpoint, params=params)
        return response.json()

    def _post(self, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """Helper method for POST requests."""
        response = self._request("POST", endpoint, params=params, data=data, json=json_data)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
             # Handle cases where response might not be JSON (e.g., 204 No Content)
            return response.text

    def _put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """Helper method for PUT requests."""
        response = self._request("PUT", endpoint, data=data, json=json_data)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text

    def _delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """Helper method for DELETE requests."""
        response = self._request("DELETE", endpoint, data=data, json=json_data)
        # DELETE often returns 204 No Content, which is not valid JSON
        if response.status_code == 204:
            return ""
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text 

