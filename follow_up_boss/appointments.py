"""
Handles the Appointments endpoints for the Follow Up Boss API.
"""

from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient


class Appointments:
    """
    A class for interacting with the Appointments endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Appointments resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_appointments(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of appointments.

        Args:
            params: Optional query parameters to filter the results.

        Returns:
            A dictionary containing the list of appointments and pagination info.
        """
        return self._client._get("appointments", params=params)

    def create_appointment(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new appointment.

        Args:
            data: A dictionary containing the appointment's details for the JSON body.
            params: Optional. Query parameters for the request.

        Returns:
            A dictionary containing the details of the created appointment or an error string.

        Note:
            According to API documentation and testing, the appointment creation
            endpoint rejects standard parameter names (date, startTime, etc.) in the request body.
            This endpoint may require specific formatting or admin permissions.
        """
        return self._client._post("appointments", json_data=data, params=params)

    def book_appointment(
        self,
        title: str,
        start_time: str,
        end_time: str,
        appointment_type_id: int,
        contacts: Optional[List[Dict[str, Any]]] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        host_user_id: Optional[int] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Books a new appointment using the Follow Up Boss calendar system.

        This is an alternative method to create_appointment that uses parameters
        that should match the API expectations.

        Args:
            title: The title of the appointment.
            start_time: The start time of the appointment (in ISO format: YYYY-MM-DDThh:mm:ss).
            end_time: The end time of the appointment (in ISO format: YYYY-MM-DDThh:mm:ss).
            appointment_type_id: The ID of the appointment type.
            contacts: Optional. List of contacts to associate with the appointment.
                Example: [{"id": 123, "type": "person"}]
            location: Optional. The location of the appointment.
            description: Optional. A description for the appointment.
            host_user_id: Optional. The ID of the user who will host the appointment.

        Returns:
            A dictionary containing the details of the booked appointment or an error string.
        """
        payload = {
            "title": title,
            "when": {"start": start_time, "end": end_time},
            "appointmentTypeId": appointment_type_id,
        }

        # Add optional fields
        if contacts:
            payload["contacts"] = contacts
        if location:
            payload["location"] = location
        if description:
            payload["description"] = description
        if host_user_id:
            payload["hostId"] = host_user_id

        return self._client._post("appointments", json_data=payload)

    def retrieve_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific appointment by its ID.

        Args:
            appointment_id: The ID of the appointment to retrieve.

        Returns:
            A dictionary containing the details of the appointment.
        """
        return self._client._get(f"appointments/{appointment_id}")

    def update_appointment(
        self, appointment_id: int, data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing appointment.

        Args:
            appointment_id: The ID of the appointment to update.
            data: A dictionary containing the fields to update.

        Returns:
            A dictionary containing the details of the updated appointment or an error string.
        """
        return self._client._put(f"appointments/{appointment_id}", json_data=data)

    def delete_appointment(self, appointment_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes an appointment.

        Args:
            appointment_id: The ID of the appointment to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self._client._delete(f"appointments/{appointment_id}")

    # GET /appointments/{id} (Retrieve appointment)
    # PUT /appointments/{id} (Update appointment)
    # DELETE /appointments/{id} (Delete appointment)
