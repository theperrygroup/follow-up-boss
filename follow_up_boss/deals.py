"""
Handles the Deals endpoints for the Follow Up Boss API.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class DealsValidationError(Exception):
    """Exception raised for deals-specific validation errors."""

    pass


class Deals:
    """
    A class for interacting with the Deals endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the Deals resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def _validate_deal_data(self, deal_data: Dict[str, Any]) -> None:
        """
        Validate deal data before API submission.

        Args:
            deal_data: The deal data to validate.

        Raises:
            DealsValidationError: If validation fails.
        """
        errors = []

        # Check for commission fields in custom_fields (common mistake)
        custom_fields = deal_data.get("custom_fields", {})
        commission_fields = ["commissionValue", "agentCommission", "teamCommission"]

        for field in commission_fields:
            if field in custom_fields:
                errors.append(
                    f"'{field}' should be a top-level parameter, not in custom_fields. "
                    f"Use {field}={custom_fields[field]} instead of custom_fields={{'{field}': {custom_fields[field]}}}"
                )

        if errors:
            raise DealsValidationError(f"Invalid deal data: {'; '.join(errors)}")

    def _normalize_field_names(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API response field names to consistent format.

        Args:
            response_data: The response data from the API.

        Returns:
            Normalized response data with consistent field names.
        """
        field_mapping = {
            "projectedCloseDate": "close_date",
            "commissionValue": "commission",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
            "userId": "user_id",
            "personId": "person_id",
            "pipelineId": "pipeline_id",
            "stageId": "stage_id",
        }

        normalized = {}
        for key, value in response_data.items():
            normalized_key = field_mapping.get(key, key)
            normalized[normalized_key] = value

        return normalized

    def _prepare_commission_data(
        self, commission_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Prepare commission data for API submission.

        Args:
            commission_data: Commission data with keys like 'total', 'agent', 'team'.

        Returns:
            Formatted commission data for API submission.
        """
        commission_fields = {}

        if "total" in commission_data:
            commission_fields["commissionValue"] = float(commission_data["total"])
        if "agent" in commission_data:
            commission_fields["agentCommission"] = float(commission_data["agent"])
        if "team" in commission_data:
            commission_fields["teamCommission"] = float(commission_data["team"])

        return commission_fields

    def set_deal_commission(
        self, deal_id: int, commission_data: Dict[str, float]
    ) -> Union[Dict[str, Any], str]:
        """
        Set commission data for an existing deal.

        Args:
            deal_id: The ID of the deal to update.
            commission_data: Commission data with keys like 'total', 'agent', 'team'.

        Returns:
            The updated deal data.

        Example:
            >>> commission_data = {
            ...     'total': 13500.0,
            ...     'agent': 9450.0,
            ...     'team': 4050.0
            ... }
            >>> deals_api.set_deal_commission(deal_id, commission_data)
        """
        commission_fields = self._prepare_commission_data(commission_data)
        return self.update_deal(deal_id, commission_fields)

    def list_deals(
        self,
        pipeline_id: Optional[int] = None,
        stage_id: Optional[int] = None,
        person_id: Optional[int] = None,
        status: Optional[str] = None,  # e.g., "Open", "Won", "Lost"
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters like price, closeDateFrom, closeDateTo
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of deals.

        Args:
            pipeline_id: Optional. Filter deals by a specific pipeline ID.
            stage_id: Optional. Filter deals by a specific stage ID.
            person_id: Optional. Filter deals associated with a specific person ID.
            status: Optional. Filter deals by status.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'closeDate', '-created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of deals and pagination information.
        """
        params: Dict[str, Any] = {}
        if pipeline_id is not None:
            params["pipeline_id"] = pipeline_id
        if stage_id is not None:
            params["stage_id"] = stage_id
        if person_id is not None:
            params["person_id"] = person_id
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)

        return self._client._get("deals", params=params)

    def create_deal(
        self,
        name: str,
        stage_id: int,
        pipeline_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        person_id: Optional[int] = None,
        price: Optional[float] = None,
        close_date: Optional[str] = None,  # YYYY-MM-DD
        description: Optional[str] = None,
        status: Optional[str] = None,
        # Commission fields as top-level parameters
        commissionValue: Optional[float] = None,
        agentCommission: Optional[float] = None,
        teamCommission: Optional[float] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new deal.

        Args:
            name: The name of the deal.
            stage_id: The ID of the stage this deal is in - REQUIRED by the API.
            pipeline_id: Optional. The ID of the pipeline this deal belongs to.
            owner_id: Optional. The User ID of the owner of this deal.
            person_id: Optional. The ID of the primary Person associated with the deal.
            price: Optional. The value of the deal.
            close_date: Optional. The expected close date (YYYY-MM-DD).
            description: Optional. A description of the deal.
            status: Optional. The status of the deal (e.g., "Active").
            commissionValue: Optional. Total commission amount.
            agentCommission: Optional. Agent's commission portion.
            teamCommission: Optional. Team's commission portion.
            **kwargs: Additional fields for the deal payload.

        Returns:
            A dictionary containing the details of the newly created deal.

        Raises:
            DealsValidationError: If commission fields are found in custom_fields.

        Example:
            >>> deal = deals_api.create_deal(
            ...     name="123 Main Street",
            ...     stage_id=26,
            ...     price=450000,
            ...     commissionValue=13500.0,
            ...     agentCommission=9450.0,
            ...     teamCommission=4050.0
            ... )
        """
        # Validate the kwargs for common mistakes
        self._validate_deal_data(kwargs)

        # Check for commission fields in custom_fields (common mistake)
        custom_fields = kwargs.get("custom_fields", {})
        commission_fields_in_custom = [
            field
            for field in ["commissionValue", "agentCommission", "teamCommission"]
            if field in custom_fields
        ]

        if commission_fields_in_custom:
            raise DealsValidationError(
                f"Commission fields {commission_fields_in_custom} found in custom_fields. "
                f"These must be passed as top-level parameters instead. "
                f"Example: create_deal(commissionValue={custom_fields[commission_fields_in_custom[0]]})"
            )

        # The API expects camelCase names with "stageId" being the only required field
        payload: Dict[str, Any] = {"name": name, "stageId": stage_id}

        # Add optional fields - note that the API rejects snake_case
        if pipeline_id is not None:
            payload["pipelineId"] = pipeline_id
        if owner_id is not None:
            payload["userId"] = owner_id  # API seems to expect userId not ownerId
        # if person_id is not None:
        #     payload["personId"] = person_id  # API rejects both contactId and personId
        if price is not None:
            payload["price"] = price
        if close_date is not None:
            payload["projectedCloseDate"] = close_date
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status

        # Add commission fields as top-level parameters
        if commissionValue is not None:
            payload["commissionValue"] = float(commissionValue)
        if agentCommission is not None:
            payload["agentCommission"] = float(agentCommission)
        if teamCommission is not None:
            payload["teamCommission"] = float(teamCommission)

        payload.update({k: v for k, v in kwargs.items() if v is not None})
        logger.debug(f"DEALS.CREATE_DEAL: Final payload before POST: {payload}")

        response = self._client._post("deals", json_data=payload)

        # Add helper properties to response
        if isinstance(response, dict):
            response["has_commission"] = bool(response.get("commissionValue"))
            response["total_people"] = len(response.get("people", []))
            response["total_users"] = len(response.get("users", []))

        return response

    def retrieve_deal(
        self, deal_id: int, normalize_fields: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves a specific deal by its ID.

        Args:
            deal_id: The ID of the deal to retrieve.
            normalize_fields: Whether to normalize field names for consistency.

        Returns:
            A dictionary containing the details of the deal.
        """
        response = self._client._get(f"deals/{deal_id}")

        if normalize_fields and isinstance(response, dict):
            response = self._normalize_field_names(response)

        return response

    def update_deal(
        self, deal_id: int, update_data: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing deal.

        Args:
            deal_id: The ID of the deal to update.
            update_data: A dictionary containing the fields to update.
                         Use camelCase for field names (e.g., {"name": "New Name", "price": 125000, "stageId": 25}).

        Returns:
            A dictionary containing the details of the updated deal.

        Raises:
            DealsValidationError: If commission fields are found in custom_fields.
        """
        # Validate the update data for common mistakes
        self._validate_deal_data(update_data)

        response = self._client._put(f"deals/{deal_id}", json_data=update_data)

        # Add helper properties to response
        if isinstance(response, dict):
            response["has_commission"] = bool(response.get("commissionValue"))
            response["total_people"] = len(response.get("people", []))
            response["total_users"] = len(response.get("users", []))

        return response

    def delete_deal(self, deal_id: int) -> Union[Dict[str, Any], str]:
        """
        Deletes a specific deal by its ID.

        Args:
            deal_id: The ID of the deal to delete.

        Returns:
            An empty dictionary if successful (API returns 204 No Content),
            or a dictionary with an error message if it fails.
        """
        return self._client._delete(f"deals/{deal_id}")

    # GET /deals/{id} (Retrieve deal)
    # PUT /deals/{id} (Update deal)
    # DELETE /deals/{id} (Delete deal)
