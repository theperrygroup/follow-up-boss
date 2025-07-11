"""
MCP (Model Context Protocol) server for Follow Up Boss API.

This module exposes Follow Up Boss API functionality as MCP tools
that can be used by AI assistants.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Try to import MCP dependencies
try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel, Field
except ImportError:
    print(
        "MCP dependencies not installed. Please run: pip install fastmcp pydantic uvloop"
    )
    sys.exit(1)

from follow_up_boss.appointments import Appointments

# Import the existing Follow Up Boss API modules
from follow_up_boss.client import FollowUpBossApiClient, FollowUpBossApiException
from follow_up_boss.custom_fields import CustomFields
from follow_up_boss.deals import Deals
from follow_up_boss.events import Events
from follow_up_boss.notes import Notes
from follow_up_boss.people import People
from follow_up_boss.pipelines import Pipelines
from follow_up_boss.stages import Stages
from follow_up_boss.tasks import Tasks
from follow_up_boss.teams import Teams
from follow_up_boss.users import Users

# Create the MCP server
mcp = FastMCP("follow-up-boss")

# Global client instance (will be initialized on startup)
_client: Optional[FollowUpBossApiClient] = None


def get_client() -> FollowUpBossApiClient:
    """Get the initialized Follow Up Boss API client.

    Returns:
        FollowUpBossApiClient: The API client instance

    Raises:
        RuntimeError: If the client is not initialized
    """
    global _client
    if _client is None:
        api_key = os.getenv("FOLLOW_UP_BOSS_API_KEY")
        x_system = os.getenv("X_SYSTEM")
        x_system_key = os.getenv("X_SYSTEM_KEY")

        if not api_key:
            raise ValueError(
                "FOLLOW_UP_BOSS_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )

        _client = FollowUpBossApiClient(
            api_key=api_key, x_system=x_system, x_system_key=x_system_key
        )
    return _client


# People Tools
@mcp.tool()
def list_people(
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
    sort: Optional[str] = Field(
        None, description="Sort field (e.g., 'name', '-created')"
    ),
    search: Optional[str] = Field(None, description="Search query"),
    includeTrash: Optional[bool] = Field(False, description="Include trashed records"),
) -> Dict[str, Any]:
    """
    List people in Follow Up Boss.

    Args:
        limit: Number of results per page (default: 50)
        offset: Number of results to skip (default: 0)
        sort: Sort field (e.g., 'name', '-created')
        search: Search query
        includeTrash: Include trashed records

    Returns:
        Dictionary containing list of people and pagination info
    """
    client = get_client()
    api = People(client)

    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if sort is not None:
        params["sort"] = sort
    if search is not None:
        params["search"] = search
    if includeTrash is not None:
        params["includeTrash"] = includeTrash

    return api.list_people(params if params else None)


@mcp.tool()
def create_person(
    name: str = Field(..., description="Person's full name"),
    emails: Optional[str] = Field(
        None, description="JSON array of email objects with 'value' key"
    ),
    phones: Optional[str] = Field(
        None, description="JSON array of phone objects with 'value' key"
    ),
    tags: Optional[str] = Field(None, description="Comma-separated list of tags"),
    source: Optional[str] = Field(None, description="Source of the lead"),
    stage: Optional[str] = Field(None, description="Stage in the pipeline"),
    assignedTo: Optional[int] = Field(None, description="User ID to assign to"),
    customFields: Optional[str] = Field(
        None, description="JSON object of custom field values"
    ),
) -> Union[Dict[str, Any], str]:
    """
    Create a new person in Follow Up Boss.

    Args:
        name: Person's full name
        emails: JSON array of email objects (e.g., '[{"value": "email@example.com"}]')
        phones: JSON array of phone objects (e.g., '[{"value": "555-1234"}]')
        tags: Comma-separated list of tags
        source: Source of the lead
        stage: Stage in the pipeline
        assignedTo: User ID to assign to
        customFields: JSON object of custom field values

    Returns:
        Dictionary containing the created person data
    """
    client = get_client()
    api = People(client)

    person_data: Dict[str, Any] = {"name": name}

    if emails:
        try:
            person_data["emails"] = json.loads(emails)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for emails parameter"}

    if phones:
        try:
            person_data["phones"] = json.loads(phones)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for phones parameter"}

    if tags:
        person_data["tags"] = [tag.strip() for tag in tags.split(",")]

    if source:
        person_data["source"] = source

    if stage:
        person_data["stage"] = stage

    if assignedTo is not None:
        person_data["assignedTo"] = assignedTo

    if customFields:
        try:
            custom_fields_data = json.loads(customFields)
            person_data.update(custom_fields_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for customFields parameter"}

    return api.create_person(person_data)


@mcp.tool()
def get_person(person_id: int = Field(..., description="Person ID")) -> Dict[str, Any]:
    """
    Get a specific person by ID.

    Args:
        person_id: Person ID

    Returns:
        Dictionary containing person data
    """
    client = get_client()
    api = People(client)
    return api.retrieve_person(person_id)


@mcp.tool()
def update_person(
    person_id: int = Field(..., description="Person ID"),
    name: Optional[str] = Field(None, description="Person's full name"),
    emails: Optional[str] = Field(None, description="JSON array of email objects"),
    phones: Optional[str] = Field(None, description="JSON array of phone objects"),
    tags: Optional[str] = Field(None, description="Comma-separated list of tags"),
    stage: Optional[str] = Field(None, description="Stage in the pipeline"),
    assignedTo: Optional[int] = Field(None, description="User ID to assign to"),
    customFields: Optional[str] = Field(
        None, description="JSON object of custom field values"
    ),
) -> Union[Dict[str, Any], str]:
    """
    Update an existing person.

    Args:
        person_id: Person ID
        name: Person's full name
        emails: JSON array of email objects
        phones: JSON array of phone objects
        tags: Comma-separated list of tags
        stage: Stage in the pipeline
        assignedTo: User ID to assign to
        customFields: JSON object of custom field values

    Returns:
        Dictionary containing updated person data
    """
    client = get_client()
    api = People(client)

    update_data: Dict[str, Any] = {}

    if name is not None:
        update_data["name"] = name

    if emails is not None:
        try:
            update_data["emails"] = json.loads(emails)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for emails parameter"}

    if phones is not None:
        try:
            update_data["phones"] = json.loads(phones)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for phones parameter"}

    if tags is not None:
        update_data["tags"] = [tag.strip() for tag in tags.split(",")]

    if stage is not None:
        update_data["stage"] = stage

    if assignedTo is not None:
        update_data["assignedTo"] = assignedTo

    if customFields:
        try:
            custom_fields_data = json.loads(customFields)
            update_data.update(custom_fields_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for customFields parameter"}

    return api.update_person(person_id, update_data)


# Notes Tools
@mcp.tool()
def create_note(
    personId: int = Field(..., description="Person ID to attach note to"),
    subject: str = Field(..., description="Note subject/title"),
    body: str = Field(..., description="Note content"),
    isHtml: Optional[bool] = Field(
        False, description="Whether the note is HTML formatted"
    ),
    typeId: Optional[int] = Field(None, description="Note type ID"),
) -> Union[Dict[str, Any], str]:
    """
    Create a note for a person.

    Args:
        personId: Person ID to attach note to
        subject: Note subject/title
        body: Note content
        isHtml: Whether the note is HTML formatted
        typeId: Note type ID

    Returns:
        Dictionary containing created note data
    """
    client = get_client()
    api = Notes(client)

    return api.create_note(
        person_id=personId, subject=subject, body=body, is_html=isHtml, type_id=typeId
    )


@mcp.tool()
def list_notes(
    personId: Optional[int] = Field(None, description="Filter by person ID"),
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List notes.

    Args:
        personId: Filter by person ID
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of notes
    """
    client = get_client()
    api = Notes(client)

    params: Dict[str, Any] = {}
    if personId is not None:
        params["personId"] = personId
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_notes(params if params else None)


# Tasks Tools
@mcp.tool()
def create_task(
    personId: int = Field(..., description="Person ID to attach task to"),
    description: str = Field(..., description="Task description"),
    dueDate: str = Field(..., description="Due date in ISO format (YYYY-MM-DD)"),
    assignedTo: Optional[int] = Field(None, description="User ID to assign task to"),
) -> Union[Dict[str, Any], str]:
    """
    Create a task.

    Args:
        personId: Person ID to attach task to
        description: Task description
        dueDate: Due date in ISO format
        assignedTo: User ID to assign task to

    Returns:
        Dictionary containing created task data
    """
    client = get_client()
    api = Tasks(client)

    task_data: Dict[str, Any] = {
        "personId": personId,
        "description": description,
        "dueDate": dueDate,
    }
    if assignedTo is not None:
        task_data["assignedTo"] = assignedTo

    return api.create_task(task_data)


@mcp.tool()
def list_tasks(
    personId: Optional[int] = Field(None, description="Filter by person ID"),
    assignedTo: Optional[int] = Field(None, description="Filter by assigned user ID"),
    includeCompleted: Optional[bool] = Field(
        False, description="Include completed tasks"
    ),
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List tasks.

    Args:
        personId: Filter by person ID
        assignedTo: Filter by assigned user ID
        includeCompleted: Include completed tasks
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of tasks
    """
    client = get_client()
    api = Tasks(client)

    params: Dict[str, Any] = {}
    if personId is not None:
        params["personId"] = personId
    if assignedTo is not None:
        params["assignedTo"] = assignedTo
    if includeCompleted is not None:
        params["includeCompleted"] = includeCompleted
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_tasks(params if params else None)


# Deals Tools
@mcp.tool()
def create_deal(
    personId: int = Field(..., description="Person ID"),
    pipelineId: int = Field(..., description="Pipeline ID"),
    stageId: int = Field(..., description="Stage ID"),
    name: str = Field(..., description="Deal name"),
    value: Optional[float] = Field(None, description="Deal value"),
    customFields: Optional[str] = Field(
        None, description="JSON object of custom field values"
    ),
) -> Union[Dict[str, Any], str]:
    """
    Create a deal.

    Args:
        personId: Person ID
        pipelineId: Pipeline ID
        stageId: Stage ID
        name: Deal name
        value: Deal value
        customFields: JSON object of custom field values

    Returns:
        Dictionary containing created deal data
    """
    client = get_client()
    api = Deals(client)

    deal_data: Dict[str, Any] = {
        "personId": personId,
        "pipelineId": pipelineId,
        "stageId": stageId,
        "name": name,
    }
    if value is not None:
        deal_data["value"] = value

    if customFields:
        try:
            custom_fields_data = json.loads(customFields)
            deal_data.update(custom_fields_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON for customFields parameter"}

    return api.create_deal(deal_data)


@mcp.tool()
def list_deals(
    personId: Optional[int] = Field(None, description="Filter by person ID"),
    pipelineId: Optional[int] = Field(None, description="Filter by pipeline ID"),
    stageId: Optional[int] = Field(None, description="Filter by stage ID"),
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List deals.

    Args:
        personId: Filter by person ID
        pipelineId: Filter by pipeline ID
        stageId: Filter by stage ID
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of deals
    """
    client = get_client()
    api = Deals(client)

    params: Dict[str, Any] = {}
    if personId is not None:
        params["personId"] = personId
    if pipelineId is not None:
        params["pipelineId"] = pipelineId
    if stageId is not None:
        params["stageId"] = stageId
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_deals(params if params else None)


# User and Team Tools
@mcp.tool()
def get_current_user() -> Union[Dict[str, Any], str]:
    """
    Get information about the current authenticated user.

    Returns:
        Dictionary containing current user data
    """
    client = get_client()
    api = Users(client)
    return api.get_me()


@mcp.tool()
def list_users(
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List all users in the organization.

    Args:
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of users
    """
    client = get_client()
    api = Users(client)

    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_users(params if params else None)


@mcp.tool()
def list_teams(
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List all teams in the organization.

    Args:
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of teams
    """
    client = get_client()
    api = Teams(client)

    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_teams(params if params else None)


# Pipeline Tools
@mcp.tool()
def list_pipelines(
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List all pipelines.

    Args:
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of pipelines
    """
    client = get_client()
    api = Pipelines(client)

    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_pipelines(params if params else None)


@mcp.tool()
def list_stages(
    pipelineId: Optional[int] = Field(None, description="Filter by pipeline ID"),
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List stages.

    Args:
        pipelineId: Filter by pipeline ID
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of stages
    """
    client = get_client()
    api = Stages(client)

    params: Dict[str, Any] = {}
    if pipelineId is not None:
        params["pipelineId"] = pipelineId
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_stages(params if params else None)


# Custom Fields Tools
@mcp.tool()
def list_custom_fields(
    limit: Optional[int] = Field(50, description="Number of results per page"),
    offset: Optional[int] = Field(0, description="Number of results to skip"),
) -> Dict[str, Any]:
    """
    List all custom fields.

    Args:
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Dictionary containing list of custom fields
    """
    client = get_client()
    api = CustomFields(client)

    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    return api.list_custom_fields(params if params else None)


# Events Tools
@mcp.tool()
def create_event(
    personId: int = Field(..., description="Person ID"),
    type: str = Field(..., description="Event type"),
    message: str = Field(..., description="Event message"),
    dateTime: Optional[str] = Field(None, description="Event date/time in ISO format"),
) -> Union[Dict[str, Any], str]:
    """
    Create an event for a person.

    Args:
        personId: Person ID
        type: Event type
        message: Event message
        dateTime: Event date/time in ISO format

    Returns:
        Dictionary containing created event data
    """
    client = get_client()
    api = Events(client)

    event_data: Dict[str, Any] = {
        "personId": personId,
        "type": type,
        "message": message,
    }
    if dateTime:
        event_data["dateTime"] = dateTime

    return api.create_event(event_data)


# Main entry point
def main() -> None:
    """Run the MCP server."""
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        print("Warning: uvloop not installed. Running with default event loop.")

    mcp.run()


if __name__ == "__main__":
    main()
