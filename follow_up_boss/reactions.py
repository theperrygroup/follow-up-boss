"""
Handles the Reactions endpoints for the Follow Up Boss API.

Reactions are emoji responses to items like notes, calls, tasks, etc.
"""

from typing import Any, Dict, Union

from .client import FollowUpBossApiClient


class Reactions:
    """
    A class for interacting with the Reactions endpoints of the Follow Up Boss API.

    Reactions are emoji responses to items (notes, calls, tasks, etc.).
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Reactions resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def create_reaction(
        self, ref_type: str, ref_id: Union[int, str], emoji: str
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a reaction on a specific item.

        Args:
            ref_type: The type of the referenced item (e.g., 'note', 'call', 'task').
            ref_id: The ID of the referenced item.
            emoji: The emoji to add as a reaction.

        Returns:
            A dictionary with the response (typically an empty array) or error string.
        """
        payload = {"body": emoji}
        return self._client._post(f"reactions/{ref_type}/{ref_id}", json_data=payload)

    def retrieve_reaction(self, reaction_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves a specific reaction by its ID.

        Args:
            reaction_id: The ID of the reaction to retrieve.

        Returns:
            A dictionary containing the details of the reaction.

        Note:
            Reaction IDs can be discovered by retrieving a note with the
            includeReactions=true parameter:
            GET /notes/{id}?includeReactions=true
        """
        return self._client._get(f"reactions/{reaction_id}")

    def delete_reaction(
        self, ref_type: str, ref_id: Union[int, str], emoji: str
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a reaction from a specific item.

        Args:
            ref_type: The type of the referenced item (e.g., 'note', 'call', 'task').
            ref_id: The ID of the referenced item.
            emoji: The emoji to remove.

        Returns:
            A dictionary with the response (typically an empty array) or error string.
        """
        payload = {"body": emoji}
        return self._client._delete(f"reactions/{ref_type}/{ref_id}", json_data=payload)
