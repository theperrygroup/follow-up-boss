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
        self.client = client

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
        return self.client._get("appointments", params=params)

    def create_appointment(self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """
        Creates a new appointment.

        Args:
            data: A dictionary containing the appointment's details for the JSON body.
            params: Optional. Query parameters for the request (e.g. startTime, endTime, appointmentTypeId)

        Returns:
            A dictionary containing the details of the created appointment or an error string.
        """
        return self.client._post("appointments", json_data=data, params=params)

    def retrieve_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific appointment by its ID.

        Args:
            appointment_id: The ID of the appointment to retrieve.

        Returns:
            A dictionary containing the details of the appointment.
        """
        return self.client._get(f"appointments/{appointment_id}")

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
        return self.client._put(f"appointments/{appointment_id}", json_data=data)

    def delete_appointment(self, appointment_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes an appointment.

        Args:
            appointment_id: The ID of the appointment to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self.client._delete(f"appointments/{appointment_id}")

    # GET /appointments/{id} (Retrieve appointment)
    # PUT /appointments/{id} (Update appointment)
    # DELETE /appointments/{id} (Delete appointment) 