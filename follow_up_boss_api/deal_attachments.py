"""
Handles the Deal Attachments endpoints for the Follow Up Boss API.
"""

import os
from typing import Dict, Any, Optional, IO, Union

# Corrected import based on the new api_client.py structure
from .client import FollowUpBossApiClient, FollowUpBossApiException

# load_dotenv is handled by ApiClient, no need to call it here directly if ApiClient manages API key loading.

class DealAttachments:
    """
    A class for interacting with the Deal Attachments part of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the DealAttachments resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def add_attachment_to_deal(
        self,
        deal_id: int,
        file: IO,
        file_name: str,
        description: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Adds an attachment to a specific deal.

        Args:
            deal_id: The ID of the deal to add the attachment to.
            file: The file object to upload.
            file_name: The name of the file.
            description: Optional description for the attachment.
            category_id: Optional ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the created attachment.

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/dealAttachments"
        data = {"dealId": str(deal_id)}
        if description:
            data["description"] = description
        if category_id is not None:
            data["categoryId"] = str(category_id)
        
        files = {"file": (file_name, file, 'application/octet-stream')} # Common MIME type for binary files
        
        # The API documentation for POST /v1/dealAttachments is not explicitly clear on whether
        # dealId, description, categoryId are part of 'data' (form fields) or 'json_data'.
        # Typically, when 'files' are involved, other parameters are sent as 'data' (form fields).
        # If the API expects these as JSON, this might need adjustment.
        # Based on POST /v1/personAttachments, it's likely form data.
        try:
            return self.client.post(endpoint, data=data, files=files)
        except FollowUpBossApiException as e:
            # Log or handle the specific "BLOCKED: API Key Permissions" scenario if needed.
            # For now, re-raise the exception.
            # Example: if "403 Forbidden" in str(e) and "API Key Permissions" in self.client.last_error_details:
            #   print("Skipping deal attachment due to API key permissions.")
            #   return {"status": "skipped", "reason": "API Key Permissions"}
            raise

    def get_deal_attachment(self, attachment_id: int) -> Union[Dict[str, Any], str]:
        """
        Retrieves a specific deal attachment.

        Args:
            attachment_id: The ID of the deal attachment to retrieve.

        Returns:
            A dictionary containing the deal attachment details.

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/dealAttachments/{attachment_id}"
        try:
            return self.client.get(endpoint)
        except FollowUpBossApiException as e:
            raise

    def update_deal_attachment(
        self,
        attachment_id: int,
        description: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Updates a specific deal attachment.

        Args:
            attachment_id: The ID of the deal attachment to update.
            description: Optional new description for the attachment.
            category_id: Optional new ID of the category for the attachment.

        Returns:
            A dictionary containing the API response for the updated attachment.

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/dealAttachments/{attachment_id}"
        payload = {}
        if description is not None: # Allow empty string for description if intended
            payload["description"] = description
        if category_id is not None:
            payload["categoryId"] = str(category_id)
        
        if not payload:
            # Or raise a ValueError("No update parameters provided")
            return {"message": "No update parameters provided, no action taken."}

        try:
            # Assuming PUT uses JSON payload for updates, common practice.
            # If it uses form-data, change to self.client.put(endpoint, data=payload)
            return self.client.put(endpoint, json_data=payload)
        except FollowUpBossApiException as e:
            raise

    def delete_deal_attachment(self, attachment_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific deal attachment.

        Args:
            attachment_id: The ID of the deal attachment to delete.

        Returns:
            A dictionary containing the API response (usually empty on success for DELETE).

        Raises:
            FollowUpBossApiException: If the API call fails.
        """
        endpoint = f"/dealAttachments/{attachment_id}"
        try:
            return self.client.delete(endpoint)
        except FollowUpBossApiException as e:
            raise

