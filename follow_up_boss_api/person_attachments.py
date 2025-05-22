"""
API bindings for Follow Up Boss Person Attachments endpoints.
"""

import os
from typing import Any, Dict, Optional, IO

from .api_client import ApiClient, FollowUpBossApiException
import logging

logger = logging.getLogger(__name__)

class PersonAttachments:
    """
    Provides access to the Person Attachments endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the PersonAttachments resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def add_attachment(
        self,
        person_id: int,
        file_path: Optional[str] = None,
        file_object: Optional[IO[bytes]] = None,
        file_name: Optional[str] = None,
        # description: Optional[str] = None, # If API supports description or other metadata
    ) -> Dict[str, Any]:
        """
        Adds an attachment to a specific person.
        You must provide either file_path or file_object (with file_name).

        Args:
            person_id: The ID of the person to add the attachment to.
            file_path: The local path to the file to be uploaded.
            file_object: An opened file-like object (e.g., from open(path, 'rb')).
                         If used, file_name must also be provided.
            file_name: The name of the file, required if using file_object.
            # description: Optional description for the attachment.

        Returns:
            A dictionary containing the details of the newly created attachment.
        
        Raises:
            ValueError: If required file parameters are missing or conflicting.
        """
        if not file_path and not (file_object and file_name):
            raise ValueError("Either file_path or both file_object and file_name must be provided.")
        if file_path and file_object:
            raise ValueError("Provide either file_path or file_object, not both.")

        files_payload: Dict[str, Any]
        data_payload: Dict[str, Any] = {"personId": str(person_id)}
        # if description:
        #     data_payload["description"] = description

        if file_path:
            actual_file_name = os.path.basename(file_path)
            try:
                with open(file_path, "rb") as f:
                    files_payload = {"file": (actual_file_name, f)}
                    # Note: ApiClient._request needs to handle 'files' and 'data' for multipart
                    return self._client.post("/personAttachments", data=data_payload, files=files_payload)
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                raise
            except IOError as e:
                logger.error(f"IOError opening file {file_path}: {e}")
                raise
        elif file_object and file_name: # Should be true if file_path was not provided
            files_payload = {"file": (file_name, file_object)}
            return self._client.post("/personAttachments", data=data_payload, files=files_payload)
        
        # This part should ideally not be reached if logic is correct
        raise RuntimeError("Unexpected state in add_attachment logic.")

    def retrieve_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Retrieves details of a specific attachment.

        Args:
            attachment_id: The ID of the attachment to retrieve.

        Returns:
            A dictionary containing the details of the attachment.
        """
        return self._client.get(f"/personAttachments/{attachment_id}")

    def update_attachment(self, attachment_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates metadata of a specific attachment.
        Commonly, this might be used to update a file name or description.

        Args:
            attachment_id: The ID of the attachment to update.
            update_data: A dictionary containing the fields to update (e.g., {"fileName": "new_name.txt"}).
                         Refer to API documentation for supported fields.

        Returns:
            A dictionary containing the details of the updated attachment.
        """
        return self._client.put(f"/personAttachments/{attachment_id}", json_data=update_data)

    def delete_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Deletes a specific attachment by its ID.

        Args:
            attachment_id: The ID of the attachment to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/personAttachments/{attachment_id}")

    def add_attachment_to_person(
        self,
        person_id: int,
        file: IO,
        file_name: str,
        description: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Adds an attachment to a specific person.

        Args:
            person_id: The ID of the person to add the attachment to.
            file: The file object to upload (e.g., open('file.txt', 'rb')).
            file_name: The name of the file as it should appear in FUB.
            description: Optional description for the attachment.
            category_id: Optional ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the created attachment.

        Raises:
            FollowUpBossApiException: If the API call fails.
            IOError: If there's an issue with the file object.
        """
        endpoint = "/personAttachments"
        # personId is a form field for this endpoint.
        data: Dict[str, Any] = {"personId": str(person_id)}
        if description:
            data["description"] = description
        if category_id is not None:
            data["categoryId"] = str(category_id)
        
        # Ensure file object is in binary mode if not already, though it's caller's responsibility.
        # Example: file.read(0) # This would error if not readable, or if text mode and first char is multi-byte
        
        files = {"file": (file_name, file, 'application/octet-stream')}
        
        try:
            return self._client.post(endpoint, data=data, files=files)
        except FollowUpBossApiException as e:
            logger.error(f"API error adding attachment to person {person_id}: {e}")
            raise
        except Exception as e: # Catch other potential errors like issues with file stream
            logger.error(f"Unexpected error adding attachment to person {person_id} for file {file_name}: {e}")
            # Consider if this should be wrapped in FollowUpBossApiException or re-raised
            raise FollowUpBossApiException(f"File handling error for {file_name}: {str(e)}") from e

    def get_person_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific person attachment.

        Args:
            attachment_id: The ID of the person attachment to retrieve.

        Returns:
            A dictionary containing the person attachment details.

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/personAttachments/{attachment_id}"
        try:
            return self._client.get(endpoint)
        except FollowUpBossApiException as e:
            logger.error(f"API error retrieving person attachment {attachment_id}: {e}")
            raise

    def update_person_attachment(
        self,
        attachment_id: int,
        description: Optional[str] = None,
        category_id: Optional[int] = None # Assuming category_id and description can be updated
    ) -> Dict[str, Any]:
        """
        Updates a specific person attachment.
        Note: FUB documentation for PUT /personAttachments/{id} indicates it updates fileName.
        This implementation is more general, allowing description/category update if supported.
        If only fileName is updatable, this should be adjusted.

        Args:
            attachment_id: The ID of the person attachment to update.
            description: Optional new description for the attachment.
            category_id: Optional new ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the updated attachment.

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/personAttachments/{attachment_id}"
        payload = {}
        # Official docs only mention fileName for update. 
        # If description/category are not supported, they will be ignored or cause error.
        if description is not None:
            payload["description"] = description 
        if category_id is not None:
            payload["categoryId"] = str(category_id)
        
        if not payload:
            # Consider what to do if FUB API only allows fileName update.
            # This version would return if no recognized fields (desc, catId) are given.
            # If fileName must be updated, it should be a required param.
            # For now, this function won't update fileName unless explicitly added.
            raise ValueError("No update parameters (description, categoryId) provided. If updating fileName, use a different method or add it here.")

        try:
            return self._client.put(endpoint, json_data=payload)
        except FollowUpBossApiException as e:
            raise

    def delete_person_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Deletes a specific person attachment.

        Args:
            attachment_id: The ID of the person attachment to delete.

        Returns:
            A dictionary containing the API response (usually empty on success for DELETE).

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/personAttachments/{attachment_id}"
        try:
            return self._client.delete(endpoint)
        except FollowUpBossApiException as e:
            logger.error(f"API error deleting person attachment {attachment_id}: {e}")
            raise

    # GET /personAttachments/{id}
    # PUT /personAttachments/{id}
    # DELETE /personAttachments/{id} 