"""
API bindings for Follow Up Boss Deal Custom Fields endpoints.
"""

from typing import Any, Dict, Optional

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class DealCustomFields:
    """
    Provides access to the Deal Custom Fields endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the DealCustomFields resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_deal_custom_fields(
        self,
        # Add relevant filters if specified by API docs (e.g., group)
        **kwargs: Any
    ) -> Dict[str, Any]: 
        """
        Retrieves a list of custom fields defined for deals.

        Args:
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of deal custom fields.
        """
        params: Dict[str, Any] = {}
        params.update(kwargs)
        
        return self._client.get("/dealCustomFields", params=params)

    def create_deal_custom_field(
        self,
        name: str,
        type: str, # E.g., "Text", "Date", "Number", "Dropdown"
        options: Optional[list[str]] = None, # Required if type is "Dropdown"
        # entityType is implicitly "Deal" for this endpoint group
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new custom field specifically for deals.

        Args:
            name: The name of the custom field.
            type: The data type of the custom field (Text, Date, Number, Dropdown).
            options: Optional. A list of string options, required if type is "Dropdown".
            **kwargs: Additional fields for the payload.

        Returns:
            A dictionary containing the details of the newly created deal custom field.
        
        Raises:
            ValueError: If type is "Dropdown" and options are not provided.
        """
        if type.lower() == "dropdown" and not options:
            raise ValueError("Argument 'options' is required when custom field type is 'Dropdown'.")

        payload: Dict[str, Any] = {
            "name": name,
            "type": type,
            # "entityType": "Deal" # Usually implied by the endpoint itself
        }
        if options:
            payload["options"] = options
        
        payload.update(kwargs)
        
        return self._client.post("/dealCustomFields", json_data=payload)

    def retrieve_deal_custom_field(self, field_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific deal custom field by its ID.

        Args:
            field_id: The ID of the deal custom field to retrieve.

        Returns:
            A dictionary containing the details of the deal custom field.
        """
        return self._client.get(f"/dealCustomFields/{field_id}")

    def update_deal_custom_field(self, field_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing deal custom field.

        Args:
            field_id: The ID of the deal custom field to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name"}).

        Returns:
            A dictionary containing the details of the updated deal custom field.
        """
        return self._client.put(f"/dealCustomFields/{field_id}", json_data=update_data)

    def delete_deal_custom_field(self, field_id: int) -> Dict[str, Any]:
        """
        Deletes a specific deal custom field by its ID.

        Args:
            field_id: The ID of the deal custom field to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client.delete(f"/dealCustomFields/{field_id}")

    # GET /dealCustomFields/{id} (Retrieve deal custom field)
    # PUT /dealCustomFields/{id} (Update deal custom field)
    # DELETE /dealCustomFields/{id} (Delete deal custom field) 