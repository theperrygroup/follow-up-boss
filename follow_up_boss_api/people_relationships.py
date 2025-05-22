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
        self.client = client

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
        return self.client._get("peopleRelationships", params=params)

    def create_people_relationship(
        self, person_id: int, related_person_id: int, relationship_type: str
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new relationship between two people.

        Args:
            person_id: The ID of the first person in the relationship.
            related_person_id: The ID of the second person in the relationship.
            relationship_type: The type of relationship (e.g., "Spouse", "Partner").

        Returns:
            A dictionary containing the details of the created relationship or an error string.
        """
        payload = {
            "personId": person_id,
            "relatedPerson": {"id": related_person_id},
            "type": relationship_type
        }
        return self.client._post("peopleRelationships", json_data=payload)

    def retrieve_people_relationship(self, relationship_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific people relationship by its ID.

        Args:
            relationship_id: The ID of the relationship to retrieve.

        Returns:
            A dictionary containing the details of the relationship.
        """
        return self.client._get(f"peopleRelationships/{relationship_id}")

    def update_people_relationship(
        self, relationship_id: int, relationship_type: str # Typically only type is updatable
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing people relationship (usually just the type).

        Args:
            relationship_id: The ID of the relationship to update.
            relationship_type: The new type for the relationship.

        Returns:
            A dictionary containing the details of the updated relationship or an error string.
        """
        payload = {"type": relationship_type}
        return self.client._put(f"peopleRelationships/{relationship_id}", json_data=payload)

    def delete_people_relationship(self, relationship_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a people relationship.

        Args:
            relationship_id: The ID of the relationship to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self.client._delete(f"peopleRelationships/{relationship_id}")

    # POST /peopleRelationships (Create people relationship)
    # GET /peopleRelationships/{id} (Retrieve people relationship)
    # PUT /peopleRelationships/{id} (Update people relationship)
    # DELETE /peopleRelationships/{id} (Delete people relationship) 