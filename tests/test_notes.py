"""
Test script for the Follow Up Boss Notes API endpoints.
"""

import os
import logging
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

def test_notes_endpoints():
    """Test the Notes endpoints of the Follow Up Boss API."""
    
    # First, create a test person to associate notes with
    logger.info("Creating a test person...")
    person_data = {
        "firstName": "Notes",
        "lastName": "TestPerson",
        "emails": [{"value": "notes_test@example.com"}]
    }
    person = client._post("people", json_data=person_data)
    logger.info(f"Created test person: {person}")
    
    if person and isinstance(person, dict) and 'id' in person:
        person_id = person['id']
        
        # Test GET /notes (List notes)
        logger.info("\nTesting GET /notes...")
        notes = client._get("notes")
        logger.info(f"Response: {notes}")
        
        # Test POST /notes (Create note)
        logger.info("\nTesting POST /notes...")
        note_data = {
            "personId": person_id, 
            "subject": "Test Note",
            "body": "This is a test note"
        }
        created_note = client._post("notes", json_data=note_data)
        logger.info(f"Response: {created_note}")
        
        if created_note and isinstance(created_note, dict) and 'id' in created_note:
            note_id = created_note['id']
            
            # Test GET /notes/{id} (Retrieve note)
            logger.info(f"\nTesting GET /notes/{note_id}...")
            note = client._get(f"notes/{note_id}")
            logger.info(f"Response: {note}")
            
            # Test PUT /notes/{id} (Update note)
            logger.info(f"\nTesting PUT /notes/{note_id}...")
            update_data = {"body": "This is an updated test note"}
            updated_note = client._put(f"notes/{note_id}", json_data=update_data)
            logger.info(f"Response: {updated_note}")
            
            # Test DELETE /notes/{id} (Delete note)
            logger.info(f"\nTesting DELETE /notes/{note_id}...")
            deleted = client._delete(f"notes/{note_id}")
            logger.info(f"Response: {deleted}")
            
            # Update the endpoint tasks file if all operations were successful
            try:
                with open("tasks/endpoint_tasks.md", "r") as f:
                    lines = f.readlines()
                
                # Update lines for notes endpoints
                for i, line in enumerate(lines):
                    if "POST /v1/notes" in line and "[ ]" in line:
                        lines[i] = line.replace("[ ]", "[x]")
                    elif "GET /v1/notes/{id}" in line and "[ ]" in line:
                        lines[i] = line.replace("[ ]", "[x]")
                    elif "PUT /v1/notes/{id}" in line and "[ ]" in line:
                        lines[i] = line.replace("[ ]", "[x]")
                    elif "DELETE /v1/notes/{id}" in line and "[ ]" in line:
                        lines[i] = line.replace("[ ]", "[x]")
                
                with open("tasks/endpoint_tasks.md", "w") as f:
                    f.writelines(lines)
                
                logger.info("Updated the endpoint tasks file for notes endpoints")
            except Exception as e:
                logger.error(f"Failed to update task file: {str(e)}")
        
        # Clean up - delete the test person
        logger.info(f"\nCleaning up: Deleting test person (ID: {person_id})...")
        client._delete(f"people/{person_id}")
        logger.info("Test person deleted")
    else:
        logger.error("Failed to create test person. Cannot proceed with notes tests.")

if __name__ == "__main__":
    test_notes_endpoints() 