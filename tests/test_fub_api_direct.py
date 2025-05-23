"""
Direct test of the Follow Up Boss API for deals.

This file tests the deals API directly without using the wrapper code
to see the raw error message and identify the correct field name format.
"""

import os
import requests
import json
import base64
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load API key from .env file
from dotenv import load_dotenv
load_dotenv()

# API credentials
API_KEY = os.getenv("FOLLOW_UP_BOSS_API_KEY")
X_SYSTEM = os.getenv("X_SYSTEM")
X_SYSTEM_KEY = os.getenv("X_SYSTEM_KEY")

# Base URL for Follow Up Boss API
BASE_URL = "https://api.followupboss.com/v1"

def test_deals_api_directly():
    """Test the deals endpoint directly with different field naming conventions."""
    
    # API key authentication (API Key as username, empty password)
    auth = (API_KEY, "")
    
    # Basic headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-System": X_SYSTEM,
        "X-System-Key": X_SYSTEM_KEY
    }
    
    # Get a pipeline ID
    response = requests.get(f"{BASE_URL}/pipelines", headers=headers, auth=auth)
    pipeline_data = response.json()
    
    if 'pipelines' not in pipeline_data or not pipeline_data['pipelines']:
        logger.error("No pipelines found")
        return
    
    pipeline_id = pipeline_data['pipelines'][0]['id']
    
    # Get a stage ID from the pipeline
    response = requests.get(f"{BASE_URL}/pipelines/{pipeline_id}", headers=headers, auth=auth)
    pipeline_detail = response.json()
    
    if 'stages' not in pipeline_detail or not pipeline_detail['stages']:
        logger.error("No stages found in pipeline")
        return
    
    stage_id = pipeline_detail['stages'][0]['id']
    
    # Get a user ID
    response = requests.get(f"{BASE_URL}/users", headers=headers, auth=auth)
    users_data = response.json()
    
    if 'users' not in users_data or not users_data['users']:
        logger.error("No users found")
        return
    
    user_id = users_data['users'][0]['id']
    
    # Get a person ID
    response = requests.get(f"{BASE_URL}/people?limit=1", headers=headers, auth=auth)
    people_data = response.json()
    
    if 'people' not in people_data or not people_data['people']:
        logger.error("No people found")
        return
    
    person_id = people_data['people'][0]['id']
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Test 5: Minimal payload with just stageId
    stage_only_payload = {
        "name": f"Stage Only Deal {timestamp}",
        "stageId": stage_id
    }
    
    logger.info(f"Testing stageId only payload: {stage_only_payload}")
    response = requests.post(f"{BASE_URL}/deals", headers=headers, auth=auth, json=stage_only_payload)
    logger.info(f"stageId only response status: {response.status_code}")
    try:
        logger.info(f"stageId only response: {response.json()}")
    except:
        logger.info(f"stageId only response text: {response.text}")
    
    # Test 6: Follow conventional format but without stageId to see exact error
    no_stage_payload = {
        "name": f"No Stage Deal {timestamp}",
        "pipeline": pipeline_id,
        "owner": user_id
    }
    
    logger.info(f"Testing payload without stageId: {no_stage_payload}")
    response = requests.post(f"{BASE_URL}/deals", headers=headers, auth=auth, json=no_stage_payload)
    logger.info(f"No stageId response status: {response.status_code}")
    try:
        logger.info(f"No stageId response: {response.json()}")
    except:
        logger.info(f"No stageId response text: {response.text}")
    
    # Test 7: Try with all possible field combinations
    all_fields_payload = {
        "name": f"All Fields Deal {timestamp}",
        "stageId": stage_id,
        "stage_id": stage_id,
        "stage": stage_id,
        "pipelineId": pipeline_id,
        "pipeline_id": pipeline_id,
        "pipeline": pipeline_id,
        "ownerId": user_id,
        "owner_id": user_id,
        "owner": user_id,
        "personId": person_id,
        "person_id": person_id,
        "person": person_id
    }
    
    logger.info(f"Testing all possible field combinations: {all_fields_payload}")
    response = requests.post(f"{BASE_URL}/deals", headers=headers, auth=auth, json=all_fields_payload)
    logger.info(f"All fields response status: {response.status_code}")
    try:
        logger.info(f"All fields response: {response.json()}")
    except:
        logger.info(f"All fields response text: {response.text}")

if __name__ == "__main__":
    test_deals_api_directly() 