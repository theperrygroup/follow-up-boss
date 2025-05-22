"""
API bindings for Follow Up Boss Custom Fields endpoints.
"""

from typing import Any, Dict, Optional

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class CustomFields:
    """
    Provides access to the Custom Fields endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the CustomFields resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_custom_fields(
        self,
        # Add relevant filters if specified by API docs (e.g., entityType, group)
        **kwargs: Any
    ) -> Dict[str, Any]: # Response is likely a list of custom field definitions
        """
        Retrieves a list of custom fields defined in the account.

        Args:
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of custom fields. 
            The FUB API often returns {"customFields": [...]} or similar.
        """
        params: Dict[str, Any] = {}
        params.update(kwargs)
        
        return self._client.get("/customFields", params=params)

    def create_custom_field(
        self,
        name: str,
        type: str, # E.g., "Text", "Date", "Number", "Dropdown"
        entity_type: str, # E.g., "Person", "Deal"
        options: Optional[list[str]] = None, # Required if type is "Dropdown"
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new custom field.

        Args:
            name: The name of the custom field.
            type: The data type of the custom field (Text, Date, Number, Dropdown).
            entity_type: The entity the custom field applies to (Person, Deal).
            options: Optional. A list of string options, required if type is "Dropdown".
            **kwargs: Additional fields for the payload.

        Returns:
            A dictionary containing the details of the newly created custom field.
        
        Raises:
            ValueError: If type is "Dropdown" and options are not provided.
        """
        if type.lower() == "dropdown" and not options:
            raise ValueError("Argument 'options' is required when custom field type is 'Dropdown'.")

        payload: Dict[str, Any] = {
            "name": name,
            "type": type,
            "entityType": entity_type
        }
        if options:
            payload["options"] = options
        
        payload.update(kwargs)
        
        return self._client.post("/customFields", json_data=payload)

    def retrieve_custom_field(self, field_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific custom field by its ID.

        Args:
            field_id: The ID of the custom field to retrieve.

        Returns:
            A dictionary containing the details of the custom field.
        """
        return self._client.get(f"/customFields/{field_id}")

    def update_custom_field(self, field_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing custom field.
        Typically, only fields like 'name' or 'options' (for dropdowns) are updatable.
        Type and entityType are usually fixed after creation.

        Args:
            field_id: The ID of the custom field to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name"}).

        Returns:
            A dictionary containing the details of the updated custom field.
        """
        return self._client.put(f"/customFields/{field_id}", json_data=update_data)

    def delete_custom_field(self, field_id: int) -> Dict[str, Any]:
        """
        Deletes a specific custom field by its ID.

        Args:
            field_id: The ID of the custom field to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/customFields/{field_id}")

    # GET /customFields/{id} (Retrieve custom field)
    # PUT /customFields/{id} (Update custom field)
    # DELETE /customFields/{id} (Delete custom field) 