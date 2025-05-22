"""
Handles the Reactions endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient
import logging

logger = logging.getLogger(__name__)

class Reactions:
    """
    A class for interacting with the Reactions endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Reactions resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def create_reaction(
        self, ref_type: str, ref_id: Union[int, str], emoji: str
    ) -> Union[List[Any], Dict[str, Any], str]: # POST returns an empty array on success, or dict/str on error
        """
        Creates a reaction on a specified reference object (e.g., Note, Call).

        Args:
            ref_type: The type of the reference object (e.g., 'Note', 'Call').
            ref_id: The ID of the reference object.
            emoji: The emoji character for the reaction (e.g., '👍').

        Returns:
            An empty list if successful, or a dictionary/string with error information.
        """
        payload = {"body": emoji}
        return self.client._post(f"reactions/{ref_type}/{ref_id}", json_data=payload)

    def retrieve_reaction(self, reaction_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific reaction by its ID.

        Note: The ID for a reaction is not returned by the create_reaction endpoint.
              Discovering reaction IDs might require other API calls or context.

        Args:
            reaction_id: The ID of the reaction to retrieve.

        Returns:
            A dictionary containing the details of the reaction.
        """
        return self.client._get(f"reactions/{reaction_id}")

    def delete_reaction(
        self, ref_type: str, ref_id: Union[int, str], emoji: str
    ) -> Union[Dict[str, Any], str]: # DELETE typically returns 204 No Content (empty string) or dict/str on error
        """
        Deletes a reaction from a specified reference object.

        Args:
            ref_type: The type of the reference object (e.g., 'Note', 'Call').
            ref_id: The ID of the reference object.
            emoji: The emoji character of the reaction to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        payload = {"body": emoji}
        # The API docs show DELETE /v1/reactions/{refType}/{refId}
        # It might expect the emoji in the body or as a query param.
        # The task list implies body: `Tested: Works (payload {"body": emoji}, not {"emoji": emoji})`
        return self.client._delete(f"reactions/{ref_type}/{ref_id}", json_data=payload) 