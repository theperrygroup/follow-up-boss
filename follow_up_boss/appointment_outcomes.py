"""
API bindings for Follow Up Boss Appointment Outcomes endpoints.
"""

import logging
from typing import Any, Dict, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class AppointmentOutcomes:
    """
    Provides access to the Appointment Outcomes endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the AppointmentOutcomes resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_appointment_outcomes(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters if specified by API docs
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Retrieves a list of appointment outcomes defined in the account.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of appointment outcomes and pagination information.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self._client._get("appointmentOutcomes", params=params)

    def create_appointment_outcome(
        self,
        name: str,
        is_successful: Optional[
            bool
        ] = None,  # Indicates if this outcome means the appointment was successful
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new appointment outcome.

        Args:
            name: The name of the appointment outcome (e.g., "Scheduled", "Completed", "Cancelled").
            is_successful: Optional. Boolean indicating if this outcome is considered a successful one.
            **kwargs: Additional fields for the payload.

        Returns:
            A dictionary containing the details of the newly created appointment outcome.
        """
        payload: Dict[str, Any] = {"name": name}
        if is_successful is not None:
            payload["isSuccessful"] = is_successful
        payload.update(kwargs)

        return self._client._post("appointmentOutcomes", json_data=payload)

    def retrieve_appointment_outcome(
        self, outcome_id: int
    ) -> Union[Dict[str, Any], str]:
        """
        Retrieves a specific appointment outcome by its ID.

        Args:
            outcome_id: The ID of the appointment outcome to retrieve.

        Returns:
            A dictionary containing the details of the appointment outcome.
        """
        return self._client._get(f"appointmentOutcomes/{outcome_id}")

    def update_appointment_outcome(
        self, outcome_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing appointment outcome.

        Args:
            outcome_id: The ID of the appointment outcome to update.
            update_data: A dictionary containing the fields to update (e.g., {"name": "New Name"}).

        Returns:
            A dictionary containing the details of the updated appointment outcome.
        """
        return self._client._put(
            f"appointmentOutcomes/{outcome_id}", json_data=update_data
        )

    def delete_appointment_outcome(
        self, outcome_id: int, assign_outcome_id: int
    ) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific appointment outcome by its ID.

        Args:
            outcome_id: The ID of the appointment outcome to delete.
            assign_outcome_id: The ID of the appointment outcome to which appointments
                              with the deleted outcome should be reassigned.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.

        Raises:
            ValueError: If assign_outcome_id is not provided, as it's required by the API.
        """
        payload = {"assignOutcomeId": assign_outcome_id}
        return self._client._delete(
            f"appointmentOutcomes/{outcome_id}", json_data=payload
        )

    # GET /appointmentOutcomes/{id} (Retrieve appointment outcome)
    # PUT /appointmentOutcomes/{id} (Update appointment outcome)
    # DELETE /appointmentOutcomes/{id} (Delete appointment outcome)
