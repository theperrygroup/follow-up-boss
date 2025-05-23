"""
API bindings for Follow Up Boss Text Messages endpoints.
"""

from typing import Any, Dict, List, Optional, Union

from .client import FollowUpBossApiClient
import logging

logger = logging.getLogger(__name__)

class TextMessages:
    """
    Provides access to the TextMessages endpoints of the Follow Up Boss API.
    
    Important Notes:
    - Phone numbers used in text messages MUST exist in the person's profile
    - Use get_person_phone_numbers() to see available numbers for a person
    - Use create_text_message_with_profile_phone() for automatic phone number selection
    """

    def __init__(self, client: FollowUpBossApiClient):
        """
        Initializes the TextMessages resource.

        Args:
            client: An instance of the FollowUpBossApiClient.
        """
        self.client = client

    def get_person_phone_numbers(self, person_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all phone numbers associated with a person.
        
        This is useful for determining which phone numbers can be used in text messages,
        as the API only accepts phone numbers that exist in the person's profile.

        Args:
            person_id: The ID of the person to get phone numbers for.

        Returns:
            A list of phone number dictionaries from the person's profile.
            Each dict contains 'value', 'type', 'status', 'isPrimary', etc.
            
        Example:
            >>> phone_numbers = text_messages.get_person_phone_numbers(900)
            >>> primary_phone = next((p['value'] for p in phone_numbers if p.get('isPrimary')), None)
        """
        person_data = self.client._get(f"people/{person_id}")
        return person_data.get('phones', [])

    def get_primary_phone_number(self, person_id: int) -> Optional[str]:
        """
        Gets the primary phone number for a person.

        Args:
            person_id: The ID of the person.

        Returns:
            The primary phone number as a string, or None if no primary phone exists.
            
        Example:
            >>> primary_phone = text_messages.get_primary_phone_number(900)
            >>> if primary_phone:
            ...     # Use this phone number for text messages
        """
        phones = self.get_person_phone_numbers(person_id)
        primary_phone = next((phone for phone in phones if phone.get('isPrimary')), None)
        return primary_phone.get('value') if primary_phone else None

    def validate_phone_number_for_person(self, person_id: int, phone_number: str) -> bool:
        """
        Validates that a phone number exists in the person's profile.
        
        This helps prevent the common error of using phone numbers that don't exist
        in the person's profile, which the API will reject.

        Args:
            person_id: The ID of the person.
            phone_number: The phone number to validate.

        Returns:
            True if the phone number exists in the person's profile, False otherwise.
            
        Example:
            >>> is_valid = text_messages.validate_phone_number_for_person(900, "8015849998")
            >>> if not is_valid:
            ...     print("Phone number not found in person's profile!")
        """
        phones = self.get_person_phone_numbers(person_id)
        person_phone_numbers = [phone.get('value', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '') 
                               for phone in phones]
        clean_input = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
        
        return any(clean_input in person_phone for person_phone in person_phone_numbers)

    def list_text_messages(
        self,
        person_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        # Add other relevant filters (e.g., direction, status, date ranges)
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Retrieves a list of text messages.

        Args:
            person_id: Filter text messages for a specific person ID.
            limit: The maximum number of results to return.
            offset: The number of results to skip for pagination.
            sort: The field to sort by (e.g., 'created', '-created').
            **kwargs: Additional query parameters to filter the results.

        Returns:
            A dictionary containing the list of text messages and pagination information.
        """
        params: Dict[str, Any] = {}
        params["personId"] = person_id 
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort is not None:
            params["sort"] = sort
        params.update(kwargs)
        
        return self.client._get("textMessages", params=params)

    def create_text_message(
        self,
        person_id: int,
        message: str,
        to_number: str,
        from_number: Optional[str] = None,
        contact_id: Optional[Union[int, str]] = None, 
        is_incoming: Optional[bool] = False,
        validate_phone: bool = True,
        **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a new text message log.
        
        IMPORTANT: Phone numbers used in text messages MUST exist in the person's profile.
        The API will reject requests with phone numbers not associated with the person.

        Args:
            person_id: The ID of the person associated with the text message.
            message: The content of the text message.
            to_number: The phone number the message is sent to. Must exist in person's profile
                      if is_incoming=False, or in system if is_incoming=True.
            from_number: Optional. The phone number the message is sent from.
            contact_id: Optional. The ID of the FUB user or FUB phone number.
            is_incoming: Boolean indicating if message is incoming (True) or outgoing (False). 
                        Defaults to False (outgoing).
            validate_phone: Whether to validate phone numbers against person's profile.
                           Defaults to True for safety.
            **kwargs: Additional fields for the text message payload.

        Returns:
            A dictionary containing the details of the newly created text message log or error string.
            
        Raises:
            ValueError: If validate_phone=True and phone numbers are not in person's profile.
            
        Example:
            >>> # Get person's phone numbers first
            >>> phones = text_messages.get_person_phone_numbers(900)
            >>> jane_phone = phones[0]['value']  # Use existing phone from profile
            >>> 
            >>> # Create outgoing message
            >>> result = text_messages.create_text_message(
            ...     person_id=900,
            ...     message="See you at the open house!",
            ...     to_number=jane_phone,
            ...     from_number="5559876543",
            ...     is_incoming=False
            ... )
        """
        # Validate phone numbers if requested
        if validate_phone:
            if not is_incoming and not self.validate_phone_number_for_person(person_id, to_number):
                available_phones = self.get_person_phone_numbers(person_id)
                phone_list = [p.get('value') for p in available_phones]
                raise ValueError(
                    f"Phone number '{to_number}' not found in person {person_id}'s profile. "
                    f"Available phone numbers: {phone_list}. "
                    f"Use get_person_phone_numbers({person_id}) to see all available numbers."
                )
            elif is_incoming and not self.validate_phone_number_for_person(person_id, from_number or ""):
                available_phones = self.get_person_phone_numbers(person_id)
                phone_list = [p.get('value') for p in available_phones]
                raise ValueError(
                    f"Phone number '{from_number}' not found in person {person_id}'s profile. "
                    f"Available phone numbers: {phone_list}. "
                    f"For incoming messages, from_number must be in the person's profile."
                )

        payload: Dict[str, Any] = {
            "personId": person_id,
            "message": message,
            "isIncoming": is_incoming,
            "toNumber": to_number
        }
        if from_number is not None:
            payload["fromNumber"] = from_number
        if contact_id is not None:
            payload["contactId"] = contact_id 
        
        payload.update(kwargs)
        
        try:
            return self.client._post("textMessages", json_data=payload)
        except Exception as e:
            # Enhance error message if it's about invalid phone numbers
            if "must be a valid phone number" in str(e).lower():
                available_phones = self.get_person_phone_numbers(person_id)
                phone_list = [p.get('value') for p in available_phones]
                enhanced_msg = (
                    f"Invalid phone number. The Follow Up Boss API requires phone numbers "
                    f"that exist in the person's profile. Person {person_id} has these phone numbers: {phone_list}. "
                    f"Original error: {e}"
                )
                raise ValueError(enhanced_msg) from e
            raise

    def create_text_message_with_profile_phone(
        self,
        person_id: int,
        message: str,
        from_number: str,
        is_incoming: bool = False,
        use_primary: bool = True,
        **kwargs: Any
    ) -> Union[Dict[str, Any], str]:
        """
        Creates a text message using a phone number from the person's profile.
        
        This is a convenience method that automatically selects an appropriate phone
        number from the person's profile, eliminating the guesswork.

        Args:
            person_id: The ID of the person.
            message: The content of the text message.
            from_number: The phone number the message is sent from (agent's number).
            is_incoming: Whether this is an incoming message from the person.
            use_primary: Whether to use the primary phone number. If False, uses first available.
            **kwargs: Additional fields for the text message payload.

        Returns:
            A dictionary containing the details of the newly created text message log or error string.
            
        Raises:
            ValueError: If the person has no phone numbers in their profile.
            
        Example:
            >>> # Automatically use person's primary phone number
            >>> result = text_messages.create_text_message_with_profile_phone(
            ...     person_id=900,
            ...     message="Thanks for your interest in the property!",
            ...     from_number="5559876543",
            ...     is_incoming=False
            ... )
        """
        phones = self.get_person_phone_numbers(person_id)
        if not phones:
            raise ValueError(f"Person {person_id} has no phone numbers in their profile. "
                           f"Add a phone number to the person's profile before sending text messages.")
        
        if use_primary:
            person_phone = self.get_primary_phone_number(person_id)
            if not person_phone:
                # Fall back to first phone if no primary
                person_phone = phones[0].get('value')
        else:
            person_phone = phones[0].get('value')
            
        if not person_phone:
            raise ValueError(f"Could not determine phone number for person {person_id}. "
                           f"Phone numbers in profile: {[p.get('value') for p in phones]}")
            
        if is_incoming:
            return self.create_text_message(
                person_id=person_id,
                message=message,
                to_number=from_number,
                from_number=person_phone,
                is_incoming=True,
                validate_phone=False,  # We already validated by getting from profile
                **kwargs
            )
        else:
            return self.create_text_message(
                person_id=person_id,
                message=message,
                to_number=person_phone,
                from_number=from_number,
                is_incoming=False,
                validate_phone=False,  # We already validated by getting from profile
                **kwargs
            )

    def retrieve_text_message(self, text_message_id: int) -> Dict[str, Any]:
        """
        Retrieves a specific text message log by its ID.

        Args:
            text_message_id: The ID of the text message log to retrieve.

        Returns:
            A dictionary containing the details of the text message log.
        """
        return self.client._get(f"textMessages/{text_message_id}")

    # GET /textMessages/{id} (Retrieve text message) 