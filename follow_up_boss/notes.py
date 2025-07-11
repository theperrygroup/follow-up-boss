"""
Handles the Notes endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient


class Notes:
    """
    A class for interacting with the Notes endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Notes resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_notes(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a list of notes.

        Args:
            params: Optional query parameters to filter the results.
                    (e.g., personId, type, limit, offset)

        Returns:
            A dictionary containing the list of notes and pagination info.
        """
        return self._client._get("notes", params=params)

    def create_note(
        self,
        person_id: int,
        subject: str,
        body: str,
        is_html: Optional[bool] = None,
        type_id: Optional[int] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new note for a specific person.

        Args:
            person_id: The ID of the person to associate the note with.
            subject: The subject/title of the note.
            body: The content of the note.
            is_html: Optional. Whether the note body is HTML. Defaults to False if not provided.
            type_id: Optional. The ID of the note type.

        Returns:
            A dictionary containing the details of the created note or an error string.
        """
        payload = {
            "personId": person_id,
            "subject": subject,
            "body": body,
        }
        if is_html is not None:
            payload["isHtml"] = is_html
        if type_id is not None:
            payload["typeId"] = type_id
        return self._client._post("notes", json_data=payload)

    def create_note_from_dict(
        self, note_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new note using a dictionary of note data.

        This is a more flexible alternative to create_note when you have a dictionary
        of note data already prepared.

        Args:
            note_data: A dictionary containing the note data. Must include at minimum:
                      - personId: The ID of the person to associate the note with
                      - subject: The subject/title of the note
                      - body: The content of the note

        Returns:
            A dictionary containing the details of the created note or an error string.

        Raises:
            ValueError: If required fields are missing from note_data.
        """
        required_fields = ["personId", "subject", "body"]
        for field in required_fields:
            if field not in note_data:
                raise ValueError(f"Missing required field '{field}' in note_data")

        return self._client._post("notes", json_data=note_data)

    def retrieve_note(
        self, note_id: int, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a specific note by its ID.

        Args:
            note_id: The ID of the note to retrieve.
            params: Optional query parameters (e.g., includeReactions=true)

        Returns:
            A dictionary containing the details of the note.
        """
        return self._client._get(f"notes/{note_id}", params=params)

    def update_note(
        self,
        note_id: int,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        is_html: Optional[bool] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing note.

        Args:
            note_id: The ID of the note to update.
            subject: Optional. The new subject/title of the note.
            body: Optional. The new content of the note.
            is_html: Optional. Whether the new note body is HTML.

        Returns:
            A dictionary containing the details of the updated note or an error string.
        """
        payload: Dict[str, Any] = {}
        if subject is not None:
            payload["subject"] = subject
        if body is not None:
            payload["body"] = body
        if is_html is not None:
            payload["isHtml"] = is_html

        if not payload:  # Nothing to update
            # Or raise an error, or return the existing note data
            # For now, let's assume the API handles empty PUTs gracefully or we prevent them.
            # Consider returning self.retrieve_note(note_id) or raising ValueError
            return self.retrieve_note(
                note_id
            )  # Or some other appropriate response for no-op

        return self._client._put(f"notes/{note_id}", json_data=payload)

    def delete_note(self, note_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a note.

        Args:
            note_id: The ID of the note to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self._client._delete(f"notes/{note_id}")

    # GET /notes/{id}
    # PUT /notes/{id}
    # DELETE /notes/{id}
