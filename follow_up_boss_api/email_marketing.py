"""
API bindings for Follow Up Boss Email Marketing endpoints.
"""

from typing import Any, Dict, Optional

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class EmailMarketing:
    """
    Provides access to the Email Marketing endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the EmailMarketing resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_email_marketing_events(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., campaignId, personId, type)
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Retrieves a list of email marketing events (e.g., opens, clicks).

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of email marketing events and pagination info.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client.get("/emEvents", params=params)

    def create_email_marketing_event(
        self,
        person_id: int,
        event_type: str, # e.g., "Sent", "Open", "Click", "Bounce", "Spam", "Unsubscribe"
        campaign_id: Optional[int] = None, # ID of the email marketing campaign
        email_id: Optional[int] = None, # ID of the specific email sent, if applicable
        url: Optional[str] = None, # For click events, the URL clicked
        # created_at: Optional[str] = None, # ISO 8601, defaults to now if not provided
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new email marketing event.

        Args:
            person_id: The ID of the person associated with the event.
            event_type: Type of the event (e.g., "Open", "Click").
            campaign_id: Optional. ID of the associated email campaign.
            email_id: Optional. ID of the specific marketing email, if different from campaign.
            url: Optional. For 'Click' events, the URL that was clicked.
            # created_at: Optional. Timestamp of the event.
            **kwargs: Additional fields for the event payload.

        Returns:
            A dictionary containing the details of the newly created event.
        """
        payload: Dict[str, Any] = {
            "personId": person_id,
            "type": event_type
        }
        if campaign_id is not None:
            payload["campaignId"] = campaign_id
        if email_id is not None:
            payload["emailId"] = email_id # Or possibly 'marketingEmailId' etc.
        if url is not None and event_type.lower() == "click":
            payload["url"] = url
        # if created_at is not None:
        #     payload["createdAt"] = created_at
        
        payload.update(kwargs)
        
        return self._client.post("/emEvents", json_data=payload)

    def list_email_marketing_campaigns(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., status, name)
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Retrieves a list of email marketing campaigns.

        Args:
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'name', 'created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of email marketing campaigns and pagination info.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client.get("/emCampaigns", params=params)

    def create_email_marketing_campaign(
        self,
        name: str,
        # Add other required fields like subject, fromName, fromEmail, listIds etc.
        # based on actual API requirements for creating a campaign.
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates a new email marketing campaign.

        Args:
            name: The name of the email marketing campaign.
            **kwargs: Additional fields for the campaign payload (e.g., subject, 
                      fromName, fromEmail, listIds, htmlBody, textBody, status).
                      Refer to FUB API documentation for required/optional fields.

        Returns:
            A dictionary containing the details of the newly created campaign.
        """
        payload: Dict[str, Any] = {
            "name": name
        }
        payload.update(kwargs)
        
        return self._client.post("/emCampaigns", json_data=payload)

    def update_email_marketing_campaign(self, campaign_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing email marketing campaign.

        Args:
            campaign_id: The ID of the campaign to update.
            update_data: A dictionary containing the fields to update 
                         (e.g., {"name": "New Campaign Name", "status": "Active"}).

        Returns:
            A dictionary containing the details of the updated campaign.
        """
        return self._client.put(f"/emCampaigns/{campaign_id}", json_data=update_data)

    # POST /emEvents (Create email marketing event)
    # GET /emCampaigns (List email marketing campaigns)
    # POST /emCampaigns (Create email marketing campaign)
    # PUT /emCampaigns/{id} (Update email marketing campaign) 