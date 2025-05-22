"""
Test script for the Follow Up Boss Calls API endpoints.
"""

import os
import logging
from datetime import datetime
import sys
from dotenv import load_dotenv
from follow_up_boss_api.client import FollowUpBossApiClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Ensure the API key is available
API_KEY = os.getenv("FOLLOW_UP_BOSS_API_KEY")
X_SYSTEM = os.getenv("X_SYSTEM")
X_SYSTEM_KEY = os.getenv("X_SYSTEM_KEY")

if not API_KEY:
    logger.error("FOLLOW_UP_BOSS_API_KEY not found in environment variables")
    sys.exit(1)

# Create a client instance
client = FollowUpBossApiClient(
    api_key=API_KEY,
    x_system=X_SYSTEM,
    x_system_key=X_SYSTEM_KEY
)

def update_task_file(endpoint: str, success: bool):
    """Update the task file to mark endpoints as completed."""
    if not success:
        return
    
    try:
        with open("tasks/endpoint_tasks.md", "r") as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if endpoint in line and "[ ]" in line:
                lines[i] = line.replace("[ ]", "[x]")
                break
        
        with open("tasks/endpoint_tasks.md", "w") as f:
            f.writelines(lines)
        
        logger.info(f"Marked {endpoint} as completed in task file")
    except Exception as e:
        logger.error(f"Failed to update task file: {str(e)}")

def test_calls_endpoints():
    """Test the Calls endpoints of the Follow Up Boss API."""
    
    # First, create a test person to associate calls with
    logger.info("Creating a test person...")
    person_data = {
        "firstName": "Calls",
        "lastName": "TestPerson",
        "emails": [{"value": "calls_test@example.com"}],
        "phones": [{"value": "555-987-6543"}]
    }
    person = client._post("people", json_data=person_data)
    logger.info(f"Created test person: {person}")
    
    if person and isinstance(person, dict) and 'id' in person:
        person_id = person['id']
        
        # Test GET /calls (List calls)
        logger.info("\nTesting GET /calls...")
        calls = client._get("calls")
        logger.info(f"Response: {calls}")
        update_task_file("GET /v1/calls", True)
        
        # Test POST /calls (Create call)
        logger.info("\nTesting POST /calls...")
        call_data = {
            "personId": person_id,
            "phone": "555-987-6543",
            "duration": 120,  # 2 minutes
            "outcome": "Interested",  # Must be one of: Interested, Not Interested, Left Message, No Answer, Busy, Bad Number
            "isIncoming": False,
            "note": "Test call via API"
        }
        created_call = client._post("calls", json_data=call_data)
        logger.info(f"Response: {created_call}")
        
        if created_call and isinstance(created_call, dict) and 'id' in created_call:
            update_task_file("POST /v1/calls", True)
            call_id = created_call['id']
            
            # Test GET /calls/{id} (Retrieve call)
            logger.info(f"\nTesting GET /calls/{call_id}...")
            call = client._get(f"calls/{call_id}")
            logger.info(f"Response: {call}")
            update_task_file("GET /v1/calls/{id}", True)
            
            # Test PUT /calls/{id} (Update call)
            logger.info(f"\nTesting PUT /calls/{call_id}...")
            update_data = {"note": "Updated test call note"}
            updated_call = client._put(f"calls/{call_id}", json_data=update_data)
            logger.info(f"Response: {updated_call}")
            update_task_file("PUT /v1/calls/{id}", True)
        
        # Clean up - delete the test person
        logger.info(f"\nCleaning up: Deleting test person (ID: {person_id})...")
        client._delete(f"people/{person_id}")
        logger.info("Test person deleted")
    else:
        logger.error("Failed to create test person. Cannot proceed with calls tests.")

if __name__ == "__main__":
    test_calls_endpoints() 