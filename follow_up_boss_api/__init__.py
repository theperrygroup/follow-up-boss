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
]

# Example of how one might initialize the client, though this might be better done in application code:
# import os
# from dotenv import load_dotenv
# load_dotenv()
# default_api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
# if default_api_key:
#     # Note: If you use this example, ensure ApiClient here refers to FollowUpBossApiClient
#     # For instance, by renaming or directly using FollowUpBossApiClient:
#     # default_client = FollowUpBossApiClient(api_key=default_api_key)
#     pass # Placeholder for example client init
# else:
#     default_client = None