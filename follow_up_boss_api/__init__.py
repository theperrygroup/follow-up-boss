"""
Follow Up Boss API Client
"""

__version__ = "0.1.0"

# Core client
from .client import FollowUpBossApiClient

# Individual API resource classes
from .appointments import Appointments
from .reactions import Reactions
from .notes import Notes
from .people import People
from .users import Users
from .appointment_types import AppointmentTypes
from .people_relationships import PeopleRelationships
from .events import Events
from .action_plans import ActionPlans
from .email_templates import EmailTemplates
from .text_message_templates import TextMessageTemplates
from .custom_fields import CustomFields
from .tasks import Tasks

__all__ = [
    "FollowUpBossApiClient",
    "Appointments",
    "Reactions",
    "Notes",
    "People",
    "Users",
    "AppointmentTypes",
    "PeopleRelationships",
    "Events",
    "ActionPlans",
    "EmailTemplates",
    "TextMessageTemplates",
    "CustomFields",
    "Tasks",
]