"""
API bindings for Follow Up Boss People endpoints.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class People:
    """
    Provides access to the People endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the People resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_people(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a list of people.

        Args:
            params: Optional query parameters to filter the results.
                      (e.g., limit, offset, sort, fields, stage, tag)

        Returns:
            A dictionary containing the list of people and pagination information.
        """
        return self._client._get("people", params=params)

    def create_person(self, person_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Creates a new person.

        Args:
            person_data: A dictionary containing the details of the person to create.

        Returns:
            A dictionary containing the details of the newly created person or an error string.
        """
        return self._client._post("people", json_data=person_data)

    def retrieve_person(
        self, person_id: int, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a specific person by their ID.

        Args:
            person_id: The ID of the person to retrieve.
            params: Optional query parameters (e.g., fields="id,name,emails").

        Returns:
            A dictionary containing the details of the person.
        """
        return self._client._get(f"people/{person_id}", params=params)

    def update_person(
        self, person_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing person.

        Args:
            person_id: The ID of the person to update.
            update_data: A dictionary containing the fields to update.

        Returns:
            A dictionary containing the details of the updated person or an error string.
        """
        return self._client._put(f"people/{person_id}", json_data=update_data)

    def delete_person(self, person_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific person by their ID.

        Args:
            person_id: The ID of the person to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self._client._delete(f"people/{person_id}")

    def check_duplicate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks for duplicate people based on provided criteria (e.g., email, phone).
        At least one identifier (email, phone) must be in params.

        Args:
            params: Query parameters (e.g., {"email": "test@example.com"}).

        Returns:
            A dictionary containing the API response.

        Raises:
            ValueError: If params is empty or missing key identifiers.
        """
        if not params or not any(key in params for key in ["email", "phone"]):
            raise ValueError(
                "Params must include at least 'email' or 'phone' to check for duplicates."
            )
        return self._client._get("people/checkDuplicate", params=params)

    def list_unclaimed_people(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of unclaimed people.

        Args:
            params: Optional query parameters (e.g., limit, offset).

        Returns:
            A dictionary containing the list of unclaimed people and pagination information.
        """
        return self._client._get("people/unclaimed", params=params)

    def claim_person(self, payload: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Claims an unclaimed person, assigning them to a user.

        Args:
            payload: Dictionary for the request body, typically including `personId`
                     and optionally `userId`.

        Returns:
            A dictionary containing the API response or an error string.
        """
        return self._client._post("people/claim", json_data=payload)

    def ignore_unclaimed_person(
        self, payload: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Marks an unclaimed person as ignored.

        Args:
            payload: Dictionary for the request body, typically including `personId`.

        Returns:
            A dictionary containing the API response or an error string.
        """
        return self._client._post("people/ignoreUnclaimed", json_data=payload)
