"""
Pytest configuration file.
"""

import os

import pytest
from dotenv import load_dotenv

from follow_up_boss.client import FollowUpBossApiClient

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def client():
    """Create a Follow Up Boss API client for testing with session scope."""
    api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
    x_system = os.getenv("X_SYSTEM")
    x_system_key = os.getenv("X_SYSTEM_KEY")

    # Ensure required environment variables are present
    if not api_key:
        pytest.fail("FOLLOW_UP_BOSS_API_KEY environment variable is not set")

    if not x_system:
        pytest.fail("X_SYSTEM environment variable is not set")

    if not x_system_key:
        pytest.fail("X_SYSTEM_KEY environment variable is not set")

    return FollowUpBossApiClient(
        api_key=api_key, x_system=x_system, x_system_key=x_system_key
    )
