"""
Follow Up Boss API Client

A comprehensive Python client library for the Follow Up Boss API.
"""

__version__ = "0.1.2"

# Core client
from .client import FollowUpBossApiClient

# Individual API resource classes
from .action_plans import ActionPlans
from .appointment_outcomes import AppointmentOutcomes
from .appointment_types import AppointmentTypes
from .appointments import Appointments
from .calls import Calls
from .custom_fields import CustomFields
from .deal_attachments import DealAttachments
from .deal_custom_fields import DealCustomFields
from .deals import Deals
from .email_marketing import EmailMarketing
from .email_templates import EmailTemplates
from .events import Events
from .groups import Groups
from .identity import Identity
from .inbox_apps import InboxApps
from .notes import Notes
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

__all__ = [
    "FollowUpBossApiClient",
    "ActionPlans",
    "AppointmentOutcomes",
    "AppointmentTypes",
    "Appointments",
    "Calls",
    "CustomFields",
    "DealAttachments",
    "DealCustomFields",
    "Deals",
    "EmailMarketing",
    "EmailTemplates",
    "Events",
    "Groups",
    "Identity",
    "InboxApps",
    "Notes",
    "People",
    "PeopleRelationships",
    "PersonAttachments",
    "Pipelines",
    "Ponds",
    "Reactions",
    "SmartLists",
    "Stages",
    "Tasks",
    "TeamInboxes",
    "Teams",
    "TextMessageTemplates",
    "TextMessages",
    "ThreadedReplies",
    "Timeframes",
    "Users",
    "WebhookEvents",
    "Webhooks",
]