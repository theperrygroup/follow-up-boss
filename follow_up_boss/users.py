"""
API bindings for Follow Up Boss Users endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class Users:
    """
    Provides access to the Users endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the Users resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_users(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a list of users in the account.

        Args:
            params: Optional query parameters to filter the results
                    (e.g., limit, offset, sort, role, status).

        Returns:
            A dictionary containing the list of users and pagination information.
        """
        return self.client._get("users", params=params)

    def retrieve_user(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific user by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A dictionary containing the details of the user.
        """
        return self.client._get(f"users/{user_id}")

    def delete_user(self, user_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific user by their ID.
        WARNING: This is a destructive operation.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        logger.warning(
            f"Attempting to delete user with ID: {user_id}. This is a destructive operation."
        )
        return self.client._delete(f"users/{user_id}")

    def get_current_user(self) -> Dict[str, Any]:
        """
        Retrieves details for the currently authenticated user (API key owner).

        Returns:
            A dictionary containing the details of the current user.
        """
        return self.client._get("me")

    # GET /users/{id} (Retrieve user)
    # GET /me (Get current user)
