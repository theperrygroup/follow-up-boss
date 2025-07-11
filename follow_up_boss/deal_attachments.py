"""
Handles the Deal Attachments endpoints for the Follow Up Boss API.
"""

import logging
import os
from typing import IO, Any, Dict, Optional, Union

# Corrected import based on the new api_client.py structure
from .client import FollowUpBossApiClient, FollowUpBossApiException

# load_dotenv is handled by ApiClient, no need to call it here directly if ApiClient manages API key loading.
logger = logging.getLogger(__name__)


class DealAttachments:
    """
    A class for interacting with the Deal Attachments part of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the DealAttachments resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def add_attachment_to_deal(
        self,
        deal_id: int,
        uri: Optional[str] = None,
        file: Optional[IO] = None,
        file_name: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Adds an attachment to a specific deal.

        There are two ways to add attachments:
        1. Provide a URI to an externally hosted file
        2. Upload a file directly (not implemented due to API constraints)

        According to the API docs: "The URI should be a link to a file location stored OUTSIDE of Follow Up Boss.
        If a URI is not provided, the API will treat the request as an attempt to upload a file to our servers and return a 403."

        Args:
            deal_id: The ID of the deal to add the attachment to.
            uri: A link to a file location stored outside of Follow Up Boss.
            file: The file object to upload (e.g., open('file.txt', 'rb')).
                  Note: Direct file upload is not implemented due to API constraints.
            file_name: The name of the file as it should appear in FUB.
            description: Optional description for the attachment.
            category_id: Optional ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the created attachment.

        Raises:
            FollowUpBossApiException: If the API call fails.
            NotImplementedError: If attempting to upload a file directly.
        """
        if file is not None:
            # TODO: Implementation requires specific API documentation on multipart upload format
            logger.warning(
                "Deal attachment direct upload is not implemented due to API constraints."
            )
            logger.warning(
                "API requires specific documentation on the exact format for file uploads."
            )
            raise NotImplementedError(
                "Deal attachment direct upload requires specific API documentation."
            )

        if not uri:
            raise ValueError(
                "Either 'uri' or 'file' must be provided. URI to external file is required."
            )

        payload: Dict[str, Any] = {"dealId": deal_id, "uri": uri}

        if description:
            payload["description"] = description
        if category_id is not None:
            payload["categoryId"] = str(
                category_id
            )  # Convert to string as the API might expect it

        return self._client._post("dealAttachments", json_data=payload)

    def get_deal_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific deal attachment.

        Args:
            attachment_id: The ID of the deal attachment to retrieve.

        Returns:
            A dictionary containing the deal attachment details.
        """
        return self._client._get(f"dealAttachments/{attachment_id}")

    def update_deal_attachment(
        self,
        attachment_id: int,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates a specific deal attachment.

        Args:
            attachment_id: The ID of the deal attachment to update.
            description: Optional new description for the attachment.
            category_id: Optional new ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the updated attachment.
        """
        payload = {}
        if description is not None:  # Allow empty string for description if intended
            payload["description"] = description
        if category_id is not None:
            payload["categoryId"] = str(
                category_id
            )  # Convert to string as the API might expect it

        if not payload:
            # Return early if no changes to make
            return {"message": "No update parameters provided, no action taken."}

        return self._client._put(f"dealAttachments/{attachment_id}", json_data=payload)

    def delete_deal_attachment(self, attachment_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific deal attachment.

        Args:
            attachment_id: The ID of the deal attachment to delete.

        Returns:
            A dictionary containing the API response (usually empty on success for DELETE).
        """
        return self._client._delete(f"dealAttachments/{attachment_id}")
