"""
Test the Timeframes API.
"""

import pytest
from follow_up_boss.client import FollowUpBossApiClient
from follow_up_boss.timeframes import Timeframes
import os

@pytest.fixture
def client():
    """Create a Follow Up Boss API client for testing."""
    return FollowUpBossApiClient(
        api_key=os.getenv("FOLLOW_UP_BOSS_API_KEY"),
        x_system=os.getenv("X_SYSTEM"),
        x_system_key=os.getenv("X_SYSTEM_KEY")
    )

@pytest.fixture
def timeframes_api(client):
    """Create a Timeframes instance for testing."""
    return Timeframes(client)

def test_list_timeframes(timeframes_api):
    """Test listing timeframes."""
    response = timeframes_api.list_timeframes()
    
    # Debug print
    print("Response:", response)
    
    # Check basic structure of the response
    assert isinstance(response, dict)
    assert '_metadata' in response
    assert 'timeframes' in response
    
    # Check metadata
    assert 'collection' in response['_metadata']
    assert response['_metadata']['collection'] == 'timeframes'
    
    # Check timeframes data
    assert isinstance(response['timeframes'], list)
    # Timeframes should always exist in the system
    assert len(response['timeframes']) > 0
    
    # Check structure of the first timeframe
    first_timeframe = response['timeframes'][0]
    assert 'id' in first_timeframe
    assert 'timeframe' in first_timeframe  # Field is 'timeframe', not 'name' 