"""
Follow Up Boss API Client

This module provides a comprehensive Python SDK for the Follow Up Boss API.
"""

from .action_plans import ActionPlans
from .appointment_outcomes import AppointmentOutcomes
from .appointment_types import AppointmentTypes
from .appointments import Appointments
from .calls import Calls
from .client import FollowUpBossApiClient, FollowUpBossApiException
from .custom_fields import CustomFields
from .deal_attachments import DealAttachments
from .deal_custom_fields import DealCustomFields
from .deals import Deals, DealsValidationError
from .email_marketing import EmailMarketing
from .email_templates import EmailTemplates

# Enhanced functionality for large-scale data operations
from .enhanced_client import (
    AuthenticationError,
    ConnectionManager,
    MaxRetriesExceeded,
    RobustApiClient,
)
from .enhanced_people import (
    EnhancedPeople,
    extract_all_people,
    extract_pond_people,
    verify_pond_extraction_quick,
)
from .events import Events
from .groups import Groups
from .identity import Identity
from .inbox_apps import InboxApps
from .notes import Notes
from .pagination import PondFilterPaginator, SmartPaginator
from .people import People
from .people_relationships import PeopleRelationships
from .person_attachments import PersonAttachments
from .pipelines import Pipelines
from .ponds import Ponds
from .reactions import Reactions
from .smart_lists import SmartLists
from .stages import Stages
from .tasks import Tasks
from .team_inboxes import TeamInboxes
from .teams import Teams
from .text_message_templates import TextMessageTemplates
from .text_messages import TextMessages
from .threaded_replies import ThreadedReplies
from .timeframes import Timeframes
from .users import Users
from .webhook_events import WebhookEvents
from .webhooks import Webhooks

__version__ = "0.2.0"
__all__ = [
    # Core API
    "FollowUpBossApiClient",
    "FollowUpBossApiException",
    "DealsValidationError",
    # Standard API Resources
    "People",
    "Deals",
    "Notes",
    "Calls",
    "TextMessages",
    "Users",
    "Events",
    "SmartLists",
    "ActionPlans",
    "EmailTemplates",
    "TextMessageTemplates",
    "EmailMarketing",
    "CustomFields",
    "Stages",
    "Tasks",
    "Appointments",
    "AppointmentTypes",
    "AppointmentOutcomes",
    "Webhooks",
    "WebhookEvents",
    "Pipelines",
    "DealAttachments",
    "DealCustomFields",
    "Groups",
    "Teams",
    "TeamInboxes",
    "Ponds",
    "InboxApps",
    "Reactions",
    "ThreadedReplies",
    "Timeframes",
    "PeopleRelationships",
    "PersonAttachments",
    "Identity",
    # Enhanced functionality for large-scale operations
    "RobustApiClient",
    "ConnectionManager",
    "AuthenticationError",
    "MaxRetriesExceeded",
    "EnhancedPeople",
    "SmartPaginator",
    "PondFilterPaginator",
    # Convenience functions
    "extract_all_people",
    "extract_pond_people",
    "verify_pond_extraction_quick",
]
