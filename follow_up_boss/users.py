"""
API bindings for Follow Up Boss Users endpoints.

This module provides comprehensive functionality for managing users and user accounts
in Follow Up Boss. It supports retrieving user information, managing user roles,
and performing user-related operations within the organization.

Key Features:
    - List and retrieve user information
    - Get current authenticated user details
    - Manage user accounts and permissions
    - Support for user role management
    - User account lifecycle operations

Usage:
    Basic usage:
        client = FollowUpBossApiClient(api_key="your_api_key")
        users = Users(client)
        
        # Get current user information
        current_user = users.get_current_user()
        
        # List all users in the organization
        all_users = users.list_users()
        
        # Get specific user details
        user = users.retrieve_user(user_id=12345)
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

        Raises:
            FollowUpBossApiException: If the API request fails.
            FollowUpBossAuthError: If authentication fails or insufficient permissions.
            FollowUpBossNotFoundError: If the user_id is not found.
            FollowUpBossValidationError: If the user cannot be deleted (e.g., has active data).
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

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The user dictionary if found, None otherwise.

        Example:
            >>> users = Users(client)
            >>> user = users.find_user_by_email("agent@example.com")
            >>> if user:
            ...     print(f"Found user: {user['name']}")
        """
        if not email:
            return None

        try:
            response = self.list_users()

            if isinstance(response, dict):
                users_list = response.get("users", [])
                email_lower = email.lower()

                for user in users_list:
                    if isinstance(user, dict):
                        user_email = user.get("email", "")
                        if user_email and user_email.lower() == email_lower:
                            return user

            return None

        except Exception as e:
            logger.error(
                f"Error searching for user by email: {e}", extra={"email": email}
            )
            return None

    def get_user_id_by_email(self, email: str) -> Optional[int]:
        """
        Find a user's ID by their email address.

        This is a convenience method that wraps find_user_by_email()
        and returns just the user ID.

        Args:
            email: The email address to search for.

        Returns:
            The user's ID if found, None otherwise.

        Example:
            >>> users = Users(client)
            >>> user_id = users.get_user_id_by_email("agent@example.com")
            >>> if user_id:
            ...     print(f"User ID: {user_id}")
        """
        user = self.find_user_by_email(email)
        if user and isinstance(user, dict):
            user_id = user.get("id")
            if user_id:
                return int(user_id)
        return None

    # GET /users/{id} (Retrieve user)
    # GET /me (Get current user)
