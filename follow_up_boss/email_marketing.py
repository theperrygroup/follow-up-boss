"""
Handles the Email Marketing endpoints for the Follow Up Boss API.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient

logger = logging.getLogger(__name__)


class EmailMarketing:
    """
    A class for interacting with the Email Marketing endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: FollowUpBossApiClient) -> None:
        """
        Initializes the EmailMarketing resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self._client = client

    def list_email_marketing_events(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of email marketing events.

        Args:
            params: Optional query parameters to filter the results.

        Returns:
            A dictionary containing the list of email marketing events.
        """
        return self._client._get("emEvents", params=params)

    def create_email_marketing_event(
        self,
        event_type: str,
        person_id: int,
        campaign_id: Optional[int] = None,
        email_id: Optional[int] = None,
        email_address: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new email marketing event.

        Args:
            event_type: The type of event (e.g., "open", "click", "unsubscribe").
            person_id: The ID of the person associated with this event.
            campaign_id: Optional. The ID of the campaign associated with this event.
            email_id: Optional. The ID of the email associated with this event.
            email_address: Optional. The email address associated with this event.
            **kwargs: Additional fields for the event.

        Returns:
            A dictionary containing the details of the newly created event.
        """
        event_data: Dict[str, Any] = {
            "type": event_type,
            "personId": person_id,
            "recipient": email_address or f"person{person_id}@example.com",
        }

        if campaign_id is not None:
            event_data["campaignId"] = campaign_id
        if email_id is not None:
            event_data["emailId"] = email_id

        event_data.update(kwargs)

        # Wrap in emEvents as expected by API
        payload = {"emEvents": [event_data]}

        return self._client._post("emEvents", json_data=payload)

    def list_email_marketing_campaigns(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of email marketing campaigns.

        Args:
            params: Optional query parameters to filter the results.

        Returns:
            A dictionary containing the list of email marketing campaigns.
        """
        return self._client._get("emCampaigns", params=params)

    def create_email_marketing_campaign(
        self, name: str, subject: str, body: str, **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new email marketing campaign.

        Args:
            name: The name of the campaign.
            subject: The subject line of the campaign.
            body: The HTML body of the campaign.
            **kwargs: Additional fields for the campaign.

        Returns:
            A dictionary containing the details of the newly created campaign.
        """
        payload: Dict[str, Any] = {
            "name": name,
            "subject": subject,
            "origin": "API",  # Required field
            "originId": 1,  # Required field - using a default value
        }

        payload.update(kwargs)

        return self._client._post("emCampaigns", json_data=payload)

    def update_email_marketing_campaign(
        self,
        campaign_id: int,
        name: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        Updates an existing email marketing campaign.

        Args:
            campaign_id: The ID of the campaign to update.
            name: Optional. The new name of the campaign.
            subject: Optional. The new subject line of the campaign.
            body: Optional. The new HTML body of the campaign.
            **kwargs: Additional fields to update.

        Returns:
            A dictionary containing the details of the updated campaign.
        """
        payload: Dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if subject is not None:
            payload["subject"] = subject
        if body is not None:
            payload["body"] = body

        payload.update(kwargs)

        return self._client._put(f"emCampaigns/{campaign_id}", json_data=payload)

    # POST /emEvents (Create email marketing event)
    # GET /emCampaigns (List email marketing campaigns)
    # POST /emCampaigns (Create email marketing campaign)
    # PUT /emCampaigns/{id} (Update email marketing campaign)
