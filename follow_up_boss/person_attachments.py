"""
API bindings for Follow Up Boss Person Attachments endpoints.
"""

import logging
import os
from typing import IO, Any, Dict, Optional, Union

import requests

from .client import FollowUpBossApiClient, FollowUpBossApiException

logger = logging.getLogger(__name__)


class PersonAttachments:
    """
    Provides access to the Person Attachments endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the PersonAttachments resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def add_attachment(
        self,
        person_id: int,
        file_path: Optional[str] = None,
        file_object: Optional[IO[bytes]] = None,
        file_name: Optional[str] = None,
        # description: Optional[str] = None, # If API supports description or other metadata
    ) -> Union[Dict[str, Any], str]:
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
            raise ValueError(
                "Either file_path or both file_object and file_name must be provided."
            )
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
                    return self._client._post(
                        "personAttachments", data=data_payload, files=files_payload
                    )
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                raise
            except IOError as e:
                logger.error(f"IOError opening file {file_path}: {e}")
                raise
        elif file_object and file_name:  # Should be true if file_path was not provided
            files_payload = {"file": (file_name, file_object)}
            return self._client._post(
                "personAttachments", data=data_payload, files=files_payload
            )

        # This part should ideally not be reached if logic is correct
        raise RuntimeError("Unexpected state in add_attachment logic.")

    def retrieve_attachment(self, attachment_id: int) -> Union[Dict[str, Any], str]:
        """
        Retrieves details of a specific attachment.

        Args:
            attachment_id: The ID of the attachment to retrieve.

        Returns:
            A dictionary containing the details of the attachment.
        """
        return self._client._get(f"personAttachments/{attachment_id}")

    def update_attachment(
        self, attachment_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
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
        return self._client._put(
            f"personAttachments/{attachment_id}", json_data=update_data
        )

    def delete_attachment(self, attachment_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific attachment by its ID.

        Args:
            attachment_id: The ID of the attachment to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client._delete(f"personAttachments/{attachment_id}")

    def add_attachment_to_person(
        self,
        person_id: int,
        file: IO,
        file_name: str,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Union[Dict[str, Any], str]:
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
            NotImplementedError: This method needs specific API documentation.
        """
        # TODO: Implementation requires specific API documentation on multipart upload format
        # The API appears to have specific requirements for file uploads that are not standard
        # We've attempted various approaches but received errors including:
        # - "Invalid fields in the request body: description, file"
        # - "Invalid fields in the request body: 0."
        logger.warning(
            "Person attachment upload is not implemented due to API constraints."
        )
        logger.warning(
            "API requires specific documentation on the exact format for file uploads."
        )
        raise NotImplementedError(
            "Person attachment upload requires specific API documentation."
        )

    def get_person_attachment(self, attachment_id: int) -> Union[Dict[str, Any], str]:
        """
        Retrieves a specific person attachment.

        Args:
            attachment_id: The ID of the person attachment to retrieve.

        Returns:
            A dictionary containing the person attachment details.

        Raises:
            FollowUpBossApiException: If the API call fails.
            NotImplementedError: This method needs specific API documentation.
        """
        # TODO: Implementation requires further API documentation
        endpoint = f"personAttachments/{attachment_id}"
        logger.warning(
            "Person attachment retrieval is not implemented due to API constraints."
        )
        raise NotImplementedError(
            "Person attachment retrieval requires specific API documentation."
        )

    def update_person_attachment(
        self,
        attachment_id: int,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates a specific person attachment.

        Args:
            attachment_id: The ID of the person attachment to update.
            description: Optional new description for the attachment.
            category_id: Optional new ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the updated attachment.

        Raises:
            FollowUpBossApiException: If the API call fails.
            NotImplementedError: This method needs specific API documentation.
        """
        # TODO: Implementation requires further API documentation
        endpoint = f"personAttachments/{attachment_id}"
        logger.warning(
            "Person attachment update is not implemented due to API constraints."
        )
        raise NotImplementedError(
            "Person attachment update requires specific API documentation."
        )

    def delete_person_attachment(
        self, attachment_id: int
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific person attachment.

        Args:
            attachment_id: The ID of the person attachment to delete.

        Returns:
            A dictionary containing the API response (usually empty on success for DELETE).

        Raises:
            FollowUpBossApiException: If the API call fails.
            NotImplementedError: This method needs specific API documentation.
        """
        # TODO: Implementation requires further API documentation
        endpoint = f"personAttachments/{attachment_id}"
        logger.warning(
            "Person attachment deletion is not implemented due to API constraints."
        )
        raise NotImplementedError(
            "Person attachment deletion requires specific API documentation."
        )

    # GET /personAttachments/{id}
    # PUT /personAttachments/{id}
    # DELETE /personAttachments/{id}
