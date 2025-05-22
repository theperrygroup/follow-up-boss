"""
Script to test Follow Up Boss API endpoints.
"""

import os
import sys
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import the client
from follow_up_boss_api.client import FollowUpBossApiClient

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
    x_system="The-Perry-Group",
    x_system_key="056749a60a8182ab7539a6bfed81569e"
)

def test_endpoint(endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Test an API endpoint and log the result.
    
    Args:
        endpoint: The API endpoint to test
        method: The HTTP method to use (GET, POST, PUT, DELETE)
        params: Optional query parameters
        data: Optional request body data
    """
    logger.info(f"Testing {method} {endpoint}")
    try:
        if method == "GET":
            response = client._get(endpoint, params=params)
        elif method == "POST":
            response = client._post(endpoint, json_data=data)
        elif method == "PUT":
            response = client._put(endpoint, json_data=data)
        elif method == "DELETE":
            response = client._delete(endpoint, json_data=data)
        else:
            logger.error(f"Unsupported method: {method}")
            return None
        
        logger.info(f"Response: {response}")
        logger.info(f"{method} {endpoint} - SUCCESS")
        return response
    except Exception as e:
        logger.error(f"{method} {endpoint} - FAILED: {str(e)}")
        return None

def update_task_file(endpoint: str, success: bool):
    """
    Update the task file to mark an endpoint as tested.
    
    Args:
        endpoint: The API endpoint that was tested
        success: Whether the test was successful
    """
    if not success:
        return
    
    try:
        # Read the task file
        with open("tasks/endpoint_tasks.md", "r") as f:
            lines = f.readlines()
        
        # Find and update the line for the tested endpoint
        for i, line in enumerate(lines):
            if endpoint in line and "[ ]" in line:
                lines[i] = line.replace("[ ]", "[x]")
                break
        
        # Write the updated file
        with open("tasks/endpoint_tasks.md", "w") as f:
            f.writelines(lines)
        
        logger.info(f"Marked {endpoint} as completed in task file")
    except Exception as e:
        logger.error(f"Failed to update task file: {str(e)}")

def test_all_endpoints():
    """Test all endpoints and mark them as working in the tasks file."""
    results = []
    
    # Test Events endpoints
    logger.info("Testing Events endpoints...")
    events = test_endpoint("events")
    success = events is not None
    results.append(("GET /v1/events", success))
    if success:
        update_task_file("GET /v1/events", True)
    
    # We need a person ID for most operations, so get one first
    # Get people to find a valid ID
    people_response = test_endpoint("people", params={"limit": 5})
    if people_response and 'people' in people_response:
        person_id = None
        for person in people_response.get('people', []):
            if 'id' in person:
                person_id = person['id']
                break
                
        # Create a test event if we have a person ID
        if person_id:
            event_data = {
                "type": "EMAIL",
                "person": {"id": person_id},
                "message": "Test event created by API"
            }
            created_event = test_endpoint("events", method="POST", data=event_data)
            success = created_event is not None
            results.append(("POST /v1/events", success))
            if success:
                update_task_file("POST /v1/events", True)
                
                # Get a specific event if one was created
                if isinstance(created_event, dict) and 'id' in created_event:
                    event_id = created_event['id']
                    event = test_endpoint(f"events/{event_id}")
                    success = event is not None
                    results.append((f"GET /v1/events/{event_id}", success))
                    if success:
                        update_task_file("GET /v1/events/{id}", True)
    
    # Test Identity endpoint
    logger.info("\nTesting Identity endpoint...")
    identity = test_endpoint("identity")
    success = identity is not None
    results.append(("GET /v1/identity", success))
    if success:
        update_task_file("GET /v1/identity", True)
    
    # Test Users endpoints
    logger.info("\nTesting Users endpoints...")
    users = test_endpoint("users")
    success = users is not None
    results.append(("GET /v1/users", success))
    if success:
        update_task_file("GET /v1/users", True)
    
    if users and 'users' in users and users['users']:
        user_id = users['users'][0]['id']
        user = test_endpoint(f"users/{user_id}")
        success = user is not None
        results.append((f"GET /v1/users/{user_id}", success))
        if success:
            update_task_file("GET /v1/users/{id}", True)
    
    # Test Me endpoint
    me = test_endpoint("me")
    success = me is not None
    results.append(("GET /v1/me", success))
    if success:
        update_task_file("GET /v1/me", True)
    
    # Test People endpoints
    logger.info("\nTesting People endpoints...")
    people = test_endpoint("people", params={"limit": 5})
    success = people is not None
    results.append(("GET /v1/people", success))
    if success:
        update_task_file("GET /v1/people", True)
    
    # Create a test person
    person_data = {
        "firstName": "Test",
        "lastName": "Person",
        "emails": [{"value": "test_person@example.com"}],
        "phones": [{"value": "555-123-4567"}]
    }
    created_person = test_endpoint("people", method="POST", data=person_data)
    success = created_person is not None
    results.append(("POST /v1/people", success))
    if success:
        update_task_file("POST /v1/people", True)
    
    # Get, update and delete the person if created
    if created_person and isinstance(created_person, dict) and 'id' in created_person:
        person_id = created_person['id']
        
        # Get the person
        person = test_endpoint(f"people/{person_id}")
        success = person is not None
        results.append((f"GET /v1/people/{person_id}", success))
        if success:
            update_task_file("GET /v1/people/{id}", True)
        
        # Update the person
        update_data = {"firstName": "Updated Test"}
        updated_person = test_endpoint(f"people/{person_id}", method="PUT", data=update_data)
        success = updated_person is not None
        results.append((f"PUT /v1/people/{person_id}", success))
        if success:
            update_task_file("PUT /v1/people/{id}", True)
        
        # Check for duplicates
        duplicates = test_endpoint("people/checkDuplicate", params={"email": "test_person@example.com"})
        success = duplicates is not None
        results.append(("GET /v1/people/checkDuplicate", success))
        if success:
            update_task_file("GET /v1/people/checkDuplicate", True)
        
        # Test unclaimed people (may be empty but API should respond)
        unclaimed = test_endpoint("people/unclaimed")
        success = unclaimed is not None
        results.append(("GET /v1/people/unclaimed", success))
        if success:
            update_task_file("GET /v1/people/unclaimed", True)
        
        # Delete the person
        deleted = test_endpoint(f"people/{person_id}", method="DELETE")
        success = deleted is not None or deleted == ""
        results.append((f"DELETE /v1/people/{person_id}", success))
        if success:
            update_task_file("DELETE /v1/people/{id}", True)
    
    # Test Notes endpoints
    logger.info("\nTesting Notes endpoints...")
    notes = test_endpoint("notes")
    success = notes is not None
    results.append(("GET /v1/notes", success))
    if success:
        update_task_file("GET /v1/notes", True)
    
    # We need a valid person ID for notes and other related endpoints
    # Create a person for testing
    test_person_data = {
        "firstName": "Note",
        "lastName": "TestPerson",
        "emails": [{"value": "note_test@example.com"}]
    }
    test_person = test_endpoint("people", method="POST", data=test_person_data)
    
    if test_person and isinstance(test_person, dict) and 'id' in test_person:
        person_id = test_person['id']
        
        # Create a note
        note_data = {
            "personId": person_id,
            "content": "Test note created via API"
        }
        created_note = test_endpoint("notes", method="POST", data=note_data)
        success = created_note is not None
        results.append(("POST /v1/notes", success))
        if success:
            update_task_file("POST /v1/notes", True)
        
        # Get and update the note if created
        if created_note and isinstance(created_note, dict) and 'id' in created_note:
            note_id = created_note['id']
            
            # Get the note
            note = test_endpoint(f"notes/{note_id}")
            success = note is not None
            results.append((f"GET /v1/notes/{note_id}", success))
            if success:
                update_task_file("GET /v1/notes/{id}", True)
            
            # Update the note
            update_note_data = {"content": "Updated test note"}
            updated_note = test_endpoint(f"notes/{note_id}", method="PUT", data=update_note_data)
            success = updated_note is not None
            results.append((f"PUT /v1/notes/{note_id}", success))
            if success:
                update_task_file("PUT /v1/notes/{id}", True)
            
            # Delete the note
            deleted_note = test_endpoint(f"notes/{note_id}", method="DELETE")
            success = deleted_note is not None or deleted_note == ""
            results.append((f"DELETE /v1/notes/{note_id}", success))
            if success:
                update_task_file("DELETE /v1/notes/{id}", True)
        
        # Clean up the test person
        test_endpoint(f"people/{person_id}", method="DELETE")
    
    # Display summary of results
    logger.info("\n=== ENDPOINT TEST RESULTS ===")
    for endpoint, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        logger.info(f"{endpoint}: {status}")

    return results

if __name__ == "__main__":
    test_all_endpoints() 