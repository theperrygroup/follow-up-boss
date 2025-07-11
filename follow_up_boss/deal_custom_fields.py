"""
Handles the Deal Custom Fields endpoints for the Follow Up Boss API.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class DealCustomFields:
    """
    A class for interacting with the Deal Custom Fields endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the DealCustomFields resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_deal_custom_fields(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of deal custom fields.

        Args:
            params: Optional query parameters to filter the results.

        Returns:
            A dictionary containing the list of deal custom fields.
        """
        return self._client._get("dealCustomFields", params=params)

    def create_deal_custom_field(
        self, name: str, field_type: str, show_in_form: bool = True, **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new deal custom field.

        Args:
            name: The name of the custom field.
            field_type: The type of the field (e.g., "text", "select", "date").
            show_in_form: Whether to show this field in forms.
            **kwargs: Additional fields for the custom field.

        Returns:
            A dictionary containing the details of the newly created custom field.

        Note:
            This operation may require admin permissions.
        """
        payload: Dict[str, Any] = {
            "name": name,
            "type": field_type,
            "showInForm": show_in_form,
        }

        payload.update(kwargs)

        return self._client._post("dealCustomFields", json_data=payload)

    def retrieve_deal_custom_field(self, field_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific deal custom field by its ID.

        Args:
            field_id: The ID of the deal custom field to retrieve.

        Returns:
            A dictionary containing the deal custom field details.
        """
        return self._client._get(f"dealCustomFields/{field_id}")

    def update_deal_custom_field(
        self,
        field_id: int,
        name: Optional[str] = None,
        field_type: Optional[str] = None,
        show_in_form: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing deal custom field.

        Args:
            field_id: The ID of the deal custom field to update.
            name: Optional. The new name of the custom field.
            field_type: Optional. The new type of the field.
            show_in_form: Optional. Whether to show this field in forms.
            **kwargs: Additional fields to update.

        Returns:
            A dictionary containing the details of the updated custom field.

        Note:
            This operation may require admin permissions.
        """
        payload: Dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if field_type is not None:
            payload["type"] = field_type
        if show_in_form is not None:
            payload["showInForm"] = show_in_form

        payload.update(kwargs)

        return self._client._put(f"dealCustomFields/{field_id}", json_data=payload)

    def delete_deal_custom_field(self, field_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific deal custom field by its ID.

        Args:
            field_id: The ID of the deal custom field to delete.

        Returns:
            An empty dictionary if successful.

        Note:
            This operation may require admin permissions.
        """
        return self._client._delete(f"dealCustomFields/{field_id}")

    # GET /dealCustomFields/{id} (Retrieve deal custom field)
    # PUT /dealCustomFields/{id} (Update deal custom field)
    # DELETE /dealCustomFields/{id} (Delete deal custom field)
