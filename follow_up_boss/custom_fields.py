"""
API bindings for Follow Up Boss Custom Fields endpoints.

Note: Creating custom fields may require admin permissions in Follow Up Boss.
The API might restrict the creation of new custom fields even with API keys that
can perform other operations. Existing custom fields can still be retrieved,
updated, and deleted with appropriate permissions.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class CustomFields:
    """
    Provides access to the Custom Fields endpoints of the Follow Up Boss API.

    Note: The creation of custom fields might be restricted based on your API key's permissions.
    Updating and listing existing custom fields should work with appropriate API access.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the CustomFields resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def list_custom_fields(
        self,
        # Add relevant filters if specified by API docs (e.g., entityType, group)
        **kwargs: Any,
    ) -> Dict[str, Any]:  # Response is likely a list of custom field definitions
        """
        Retrieves a list of custom fields defined in the account.

        Args:
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of custom fields.
            The FUB API returns {"customfields": [...]} (lowercase)
        """
        params: Dict[str, Any] = {}
        params.update(kwargs)

        return self.client._get("customFields", params=params)

    def create_custom_field(
        self,
        name: str,
        type: str,  # E.g., "text", "date", "dropdown" - must be lowercase
        entity_type: Optional[str] = None,  # E.g., "Person", "Deal"
        options: Optional[List[str]] = None,  # Required if type is "dropdown"
        label: Optional[str] = None,  # Display label for the field
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new custom field.

        Note: This operation may be restricted based on API permissions.
        Custom field creation often requires admin rights in Follow Up Boss.

        Args:
            name: The name of the custom field (should start with "custom").
            type: The data type of the custom field (text, date, dropdown) - must be lowercase.
            entity_type: Optional. The entity the custom field applies to (Person, Deal).
            options: Optional. A list of string options, required if type is "dropdown".
            label: Optional. The display label for the field.
            **kwargs: Additional fields for the payload.

        Returns:
            A dictionary containing the details of the newly created custom field or an error string.

        Raises:
            ValueError: If type is "dropdown" and options are not provided.
        """
        if type.lower() == "dropdown" and not options:
            raise ValueError(
                "Argument 'options' is required when custom field type is 'dropdown'."
            )

        # Ensure name starts with "custom" as seen in existing fields
        if not name.startswith("custom"):
            name = f"custom{name}"

        payload: Dict[str, Any] = {
            "name": name,
            "type": type.lower(),  # Ensure type is lowercase
        }

        if entity_type is not None:
            payload["entityType"] = entity_type
        if options:
            payload["options"] = options
        if label is not None:
            payload["label"] = label

        payload.update(kwargs)

        return self.client._post("customFields", json_data=payload)

    def retrieve_custom_field(self, field_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific custom field by its ID.

        Args:
            field_id: The ID of the custom field to retrieve.

        Returns:
            A dictionary containing the details of the custom field.
        """
        return self.client._get(f"customFields/{field_id}")

    def update_custom_field(
        self, field_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing custom field.
        Typically, only fields like 'label' or 'options' (for dropdowns) are updatable.
        Type is usually fixed after creation.

        Args:
            field_id: The ID of the custom field to update.
            update_data: A dictionary containing the fields to update (e.g., {"label": "New Label"}).

        Returns:
            A dictionary containing the details of the updated custom field or an error string.
        """
        return self.client._put(f"customFields/{field_id}", json_data=update_data)

    def delete_custom_field(self, field_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific custom field by its ID.

        Args:
            field_id: The ID of the custom field to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails, or an error string.
        """
        return self.client._delete(f"customFields/{field_id}")

    # GET /customFields/{id} (Retrieve custom field)
    # PUT /customFields/{id} (Update custom field)
    # DELETE /customFields/{id} (Delete custom field)
