"""
API bindings for Follow Up Boss Appointment Types endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class AppointmentTypes:
    """
    Provides access to the Appointment Types endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the AppointmentTypes resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_appointment_types(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of appointment types defined in the account.

        Args:
            params: Optional query parameters to filter the results (e.g., limit, offset, sort).

        Returns:
            A dictionary containing the list of appointment types and pagination information.
        """
        return self._client._get("appointmentTypes", params=params)

    def create_appointment_type(
        self, name: str, params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new appointment type.

        Args:
            name: The name of the appointment type.
            params: Optional. Other parameters for the appointment type payload.

        Returns:
            A dictionary containing the details of the newly created appointment type or an error string.
        """
        payload: Dict[str, Any] = {"name": name}
        if params:
            payload.update(params)

        return self._client._post("appointmentTypes", json_data=payload)

    def retrieve_appointment_type(self, appt_type_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific appointment type by its ID.

        Args:
            appt_type_id: The ID of the appointment type to retrieve.

        Returns:
            A dictionary containing the details of the appointment type.
        """
        return self._client._get(f"appointmentTypes/{appt_type_id}")

    def update_appointment_type(
        self, appt_type_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing appointment type.

        Args:
            appt_type_id: The ID of the appointment type to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name"}).

        Returns:
            A dictionary containing the details of the updated appointment type or an error string.
        """
        return self._client._put(
            f"appointmentTypes/{appt_type_id}", json_data=update_data
        )

    def delete_appointment_type(self, appt_type_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific appointment type by its ID.

        Args:
            appt_type_id: The ID of the appointment type to delete.

        Returns:
            An empty string if successful, or a dictionary/string with error information.
        """
        return self._client._delete(f"appointmentTypes/{appt_type_id}")

    # GET /appointmentTypes/{id} (Retrieve appointment type)
    # PUT /appointmentTypes/{id} (Update appointment type)
    # DELETE /appointmentTypes/{id} (Delete appointment type)
