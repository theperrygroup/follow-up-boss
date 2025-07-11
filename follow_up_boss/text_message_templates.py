"""
API bindings for Follow Up Boss Text Message Templates endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class TextMessageTemplates:
    """
    Provides access to the Text Message Templates endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the TextMessageTemplates resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_text_message_templates(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., shared)
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of text message templates.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of text message templates and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self.client._get("textMessageTemplates", params=params)

    def create_text_message_template(
        self,
        name: str,
        body: str,  # Text content of the template
        # shared: Optional[bool] = False, # If API supports 'shared' flag
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new text message template.

        Args:
            name: The name of the text message template.
            body: The content/body of the text message template.
            # shared: Optional. Whether the template is shared.
            **kwargs: Additional fields for the payload.

        Returns:
            A dictionary containing the details of the newly created template or an error string.
        """
        payload: Dict[str, Any] = {"name": name, "message": body}
        # if shared is not None:
        #     payload["shared"] = shared

        payload.update(kwargs)

        return self.client._post("textMessageTemplates", json_data=payload)

    def retrieve_text_message_template(self, template_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific text message template by its ID.

        Args:
            template_id: The ID of the text message template to retrieve.

        Returns:
            A dictionary containing the details of the text message template.
        """
        return self.client._get(f"textMessageTemplates/{template_id}")

    def update_text_message_template(
        self, template_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing text message template.

        Args:
            template_id: The ID of the text message template to update.
            update_data: A dictionary containing the fields to update
                         (e.g., {"name": "New Name", "body": "New Body"}).

        Returns:
            A dictionary containing the details of the updated template or an error string.
        """
        return self.client._put(
            f"textMessageTemplates/{template_id}", json_data=update_data
        )

    def merge_text_message_template(
        self,
        body: str,
        merge_fields: Dict[str, Any],
        template_id: Optional[int] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Merges field data into a text message template body.

        Args:
            body: The body of the text message template to merge fields into.
            merge_fields: A dictionary of merge fields and their values.
            template_id: Optional. ID of an existing template to use as the base.
            **kwargs: Additional parameters for the merge operation.

        Returns:
            A dictionary containing the merged body, or an error string.
        """
        payload: Dict[str, Any] = {"body": body, "mergeFields": merge_fields}
        if template_id is not None:
            payload["templateId"] = template_id

        payload.update(kwargs)

        return self.client._post("textMessageTemplates/merge", json_data=payload)

    def delete_text_message_template(
        self, template_id: int
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific text message template by its ID.

        Args:
            template_id: The ID of the text message template to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails, or an error string.
        """
        return self.client._delete(f"textMessageTemplates/{template_id}")

    # GET /textMessageTemplates/{id} (Retrieve text message template)
    # PUT /textMessageTemplates/{id} (Update text message template)
    # POST /textMessageTemplates/merge (Merge text message template)
    # DELETE /textMessageTemplates/{id} (Delete text message template)
