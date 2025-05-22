"""
API bindings for Follow Up Boss Events endpoints.
Events are activities related to people, such as website visits, inquiries, etc.
"""

from typing import Any, Dict, Optional, List, Union

from .api_client import ApiClient
import logging

logger = logging.getLogger(__name__)

class Events:
    """
    Provides access to the Events endpoints of the Follow Up Boss API.
    """

    def __init__(self, client: ApiClient):
        """
        Initializes the Events resource.

        Args:
            client: An instance of the ApiClient.
        """
        self._client = client

    def list_events(
        self,
        person_id: Optional[int] = None,
        type: Optional[Union[str, List[str]]] = None, # Single type or list of types
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., createdFrom, createdTo, source)
        **kwargs: Any
    ) -> Dict[str, Any]: 
        """
        Retrieves a list of events.

        Args:
            person_id: Optional. Filter events for a specific person ID.
            type: Optional. Filter events by type(s) (e.g., "Property Inquiry", ["Call", "TextMessage"]).
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'created', '-created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of events and pagination information.
        """
        params: Dict[str, Any] = {}
        if person_id is not None:
            params["personId"] = person_id
        if type is not None:
            if isinstance(type, list):
                params["type[]"] = type # API might expect type[] for multiple values
            else:
                params["type"] = type
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self._client.get("/events", params=params)

    def create_event(
        self,
        type: str, 
        person_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        source: Optional[str] = None, 
        source_url: Optional[str] = None,
        description: Optional[str] = None,
        message: Optional[str] = None, 
        property_street: Optional[str] = None,
        property_city: Optional[str] = None,
        property_state: Optional[str] = None,
        property_zip: Optional[str] = None,
        property_mls_number: Optional[str] = None,
        property_price: Optional[Union[int, float]] = None,
        campaign_name: Optional[str] = None, 
        campaign_source: Optional[str] = None, 
        campaign_medium: Optional[str] = None,
        campaign_term: Optional[str] = None,
        campaign_content: Optional[str] = None,
        **kwargs: Any 
    ) -> Dict[str, Any]:
        """
        Creates an event. This endpoint is versatile and can also create/update people.
        Args:
            type: The type of event.
            person_id: Optional. ID of an existing person to associate the event with.
            first_name, last_name, email, phone: Optional. Person details if creating/updating a person.
            source: Optional. Source of the event/lead.
            source_url: Optional. URL of the source.
            description: Optional. A general description of the event.
            message: Optional. Content for message-like events.
            property_...: Optional. Details for property-related events.
            campaign_...: Optional. UTM-style campaign tracking parameters.
            **kwargs: Allows for additional top-level fields or nested objects like 'customFields', 'tags'.
        Returns:
            A dictionary, typically representing the person associated with the event.
        """
        payload: Dict[str, Any] = {"type": type}
        person_data: Dict[str, Any] = {}
        if person_id is not None: person_data["id"] = person_id
        if first_name is not None: person_data["firstName"] = first_name
        if last_name is not None: person_data["lastName"] = last_name
        if email is not None: 
            if "emails" not in person_data: person_data["emails"] = []
            person_data["emails"].append({"value": email, "type": "unknown"})
        if phone is not None:
            if "phones" not in person_data: person_data["phones"] = []
            person_data["phones"].append({"value": phone, "type": "unknown"})
        if person_data: payload["person"] = person_data
        
        if source is not None: payload["source"] = source
        if source_url is not None: payload["sourceUrl"] = source_url
        if description is not None: payload["description"] = description
        if message is not None: payload["message"] = message

        property_data: Dict[str, Any] = {}
        if property_street is not None: property_data["street"] = property_street
        if property_city is not None: property_data["city"] = property_city
        if property_state is not None: property_data["state"] = property_state
        if property_zip is not None: property_data["zip"] = property_zip
        if property_mls_number is not None: property_data["mlsNumber"] = property_mls_number
        if property_price is not None: property_data["price"] = property_price
        if property_data: payload["property"] = property_data

        campaign_data: Dict[str, Any] = {}
        if campaign_name is not None: campaign_data["name"] = campaign_name
        if campaign_source is not None: campaign_data["source"] = campaign_source
        if campaign_medium is not None: campaign_data["medium"] = campaign_medium
        if campaign_term is not None: campaign_data["term"] = campaign_term
        if campaign_content is not None: campaign_data["content"] = campaign_content
        if campaign_data: 
            if "source" not in campaign_data and campaign_source is None:
                pass 
            payload["campaign"] = campaign_data
            
        payload.update(kwargs)
        return self._client.post("/events", json_data=payload)

    def retrieve_event(self, event_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves a specific event by its ID.

        Args:
            event_id: The ID of the event to retrieve.

        Returns:
            A dictionary containing the details of the event.
        """
        return self._client.get(f"/events/{event_id}")

    # GET /events/{id} (Retrieve event)
