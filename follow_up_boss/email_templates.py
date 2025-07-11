"""
API bindings for Follow Up Boss Email Templates endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class EmailTemplates:
    """
    Provides access to the Email Templates endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the EmailTemplates resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_email_templates(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., shared, type)
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of email templates.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of email templates and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        # Endpoint is /templates as per user-provided list
        return self.client._get("templates", params=params)

    def create_email_template(
        self,
        name: str,
        subject: str,
        body: str,  # HTML body of the email template
        # shared: Optional[bool] = False, # If API supports 'shared' flag
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new email template.

        Args:
            name: The name of the email template.
            subject: The subject line of the email template.
            body: The HTML content/body of the email template.
            # shared: Optional. Whether the template is shared. Defaults to False if applicable.
            **kwargs: Additional fields for the email template payload.

        Returns:
            A dictionary containing the details of the newly created email template or an error string.
        """
        payload: Dict[str, Any] = {"name": name, "subject": subject, "body": body}
        # if shared is not None:
        #     payload["shared"] = shared

        payload.update(kwargs)

        return self.client._post("templates", json_data=payload)

    def retrieve_email_template(self, template_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific email template by its ID.

        Args:
            template_id: The ID of the email template to retrieve.

        Returns:
            A dictionary containing the details of the email template.
        """
        return self.client._get(f"templates/{template_id}")

    def update_email_template(
        self, template_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing email template.

        Args:
            template_id: The ID of the email template to update.
            update_data: A dictionary containing the fields to update
                         (e.g., {"name": "New Name", "subject": "New Subject", "body": "New Body"}).

        Returns:
            A dictionary containing the details of the updated email template or an error string.
        """
        return self.client._put(f"templates/{template_id}", json_data=update_data)

    def merge_email_template(
        self,
        body: str,
        merge_fields: Dict[str, Any],
        template_id: Optional[int] = None,
        subject: Optional[str] = None,  # If merging subject too
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Merges field data into an email template (subject and/or body).
        This is typically used for previewing a template with specific data.

        Args:
            body: The HTML body of the email template to merge fields into.
            merge_fields: A dictionary of merge fields and their values
                          (e.g., {"firstName": "John", "lastName": "Doe"}).
            template_id: Optional. The ID of an existing template to use as the base for merging.
                         If provided, body and subject might be overridden or augmented by this template.
            subject: Optional. The subject line to merge fields into. If not provided, only body is merged,
                     or if template_id is used, its subject might be used.
            **kwargs: Additional parameters for the merge operation.

        Returns:
            A dictionary containing the merged subject and body, or an error string.
        """
        payload: Dict[str, Any] = {"body": body, "mergeFields": merge_fields}
        if template_id is not None:
            payload["templateId"] = template_id
        if subject is not None:
            payload["subject"] = subject

        payload.update(kwargs)

        return self.client._post("templates/merge", json_data=payload)

    def delete_email_template(self, template_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific email template by its ID.

        Args:
            template_id: The ID of the email template to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails, or an error string.
        """
        return self.client._delete(f"templates/{template_id}")

    # GET /templates/{id} (Retrieve email template)
    # PUT /templates/{id} (Update email template)
    # POST /templates/merge (Merge email template)
    # DELETE /templates/{id} (Delete email template)
