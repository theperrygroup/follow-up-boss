"""
Handles the People Relationships endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient


class PeopleRelationships:
    """
    A class for interacting with the People Relationships endpoints.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the PeopleRelationships resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_people_relationships(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of people relationships.

        Args:
            params: Optional query parameters to filter the results.
                    (e.g., limit, offset, sort, personId, relatedPersonId, type)

        Returns:
            A dictionary containing the list of relationships and pagination info.
        """
        return self._client._get("peopleRelationships", params=params)

    def create_people_relationship(
        self,
        person_id: int,
        relationship_type: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        emails: Optional[List[Dict[str, Any]]] = None,
        phones: Optional[List[Dict[str, Any]]] = None,
        addresses: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new relationship for a person.

        Args:
            person_id: The ID of the person to create a relationship for.
            relationship_type: The type of relationship (e.g., "Spouse", "Brother", "Partner").
            first_name: The first/given name of the relationship.
            last_name: The last/family name of the relationship.
            emails: A list of email addresses associated with the relationship.
                   Each email should be a dict with 'value' and 'type' keys.
                   Example: [{"value": "john@example.com", "type": "work"}]
            phones: A list of phone numbers associated with the relationship.
                   Each phone should be a dict with 'value' and 'type' keys.
                   Example: [{"value": "555-1234", "type": "mobile"}]
            addresses: A list of addresses associated with the relationship.
                      Each address should be a dict with address components.
            **kwargs: Additional fields to include in the request.

        Returns:
            A dictionary containing the details of the created relationship or an error string.

        Note:
            According to the API documentation, firstName, lastName, emails, phones, and addresses
            are all supported fields that can be set during relationship creation.
        """
        payload = {"personId": person_id, "type": relationship_type}

        # Add optional fields if provided
        if first_name is not None:
            payload["firstName"] = first_name
        if last_name is not None:
            payload["lastName"] = last_name
        if emails is not None:
            payload["emails"] = emails
        if phones is not None:
            payload["phones"] = phones
        if addresses is not None:
            payload["addresses"] = addresses

        # Add any additional fields from kwargs
        payload.update(kwargs)

        return self._client._post("peopleRelationships", json_data=payload)

    def retrieve_people_relationship(self, relationship_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific people relationship by its ID.

        Args:
            relationship_id: The ID of the relationship to retrieve.

        Returns:
            A dictionary containing the details of the relationship.
        """
        return self._client._get(f"peopleRelationships/{relationship_id}")

    def update_people_relationship(
        self,
        relationship_id: int,
        relationship_type: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        emails: Optional[List[Dict[str, Any]]] = None,
        phones: Optional[List[Dict[str, Any]]] = None,
        addresses: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing people relationship.

        Args:
            relationship_id: The ID of the relationship to update.
            relationship_type: The new type for the relationship (e.g., "Spouse", "Brother", "Partner").
            first_name: The first/given name of the relationship.
            last_name: The last/family name of the relationship.
            emails: A list of email addresses associated with the relationship.
                   Each email should be a dict with 'value' and 'type' keys.
                   Example: [{"value": "john@example.com", "type": "work"}]
            phones: A list of phone numbers associated with the relationship.
                   Each phone should be a dict with 'value' and 'type' keys.
                   Example: [{"value": "555-1234", "type": "mobile"}]
            addresses: A list of addresses associated with the relationship.
                      Each address should be a dict with address components.
            **kwargs: Additional fields to include in the request.

        Returns:
            A dictionary containing the details of the updated relationship or an error string.

        Important Notes:
            - To update a relationship, you must have access to the parent person.
            - The `personId` of an existing relationship CANNOT be altered after creation.
            - Sending an array of emails, phones, or addresses will OVERWRITE existing values.
            - To maintain existing contacts while adding new ones, you must include the current
              list plus any new items in the array.
            - If contact arrays are left blank/None, no changes are made to those fields.

        Warning:
            Array fields (emails, phones, addresses) completely replace existing data when provided.
            Retrieve the current relationship first if you need to preserve existing contact info.
        """
        payload: Dict[str, Any] = {}

        # Add fields that should be updated
        if relationship_type is not None:
            payload["type"] = relationship_type
        if first_name is not None:
            payload["firstName"] = first_name
        if last_name is not None:
            payload["lastName"] = last_name
        if emails is not None:
            payload["emails"] = emails
        if phones is not None:
            payload["phones"] = phones
        if addresses is not None:
            payload["addresses"] = addresses

        # Add any additional fields from kwargs
        payload.update(kwargs)

        # Ensure we have something to update
        if not payload:
            raise ValueError(
                "At least one field must be provided to update the relationship."
            )

        return self._client._put(
            f"peopleRelationships/{relationship_id}", json_data=payload
        )

    def delete_people_relationship(
        self, relationship_id: int
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a people relationship.

        Args:
            relationship_id: The ID of the relationship to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self._client._delete(f"peopleRelationships/{relationship_id}")

    # POST /peopleRelationships (Create people relationship)
    # GET /peopleRelationships/{id} (Retrieve people relationship)
    # PUT /peopleRelationships/{id} (Update people relationship)
    # DELETE /peopleRelationships/{id} (Delete people relationship)
