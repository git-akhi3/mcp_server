from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)
import json
from typing import Dict, Any

# Schema Definitions
GET_ALL_EVENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "page": {
            "type": "integer",
            "description": "Page number for pagination (0-indexed). Default is 0.",
            "default": 0
        },
        "size": {
            "type": "integer",
            "description": "Number of events per page. Default is 4.",
            "default": 4
        },
        "sortBy": {
            "type": "string",
            "description": "Field to sort by. Default is 'eventDateTime'.",
            "default": "eventDateTime"
        },
        "sortDir": {
            "type": "string",
            "description": "Sort direction: 'asc' for ascending, 'desc' for descending. Default is 'asc'.",
            "enum": ["asc", "desc"],
            "default": "asc"
        },
        "afterDate": {
            "type": "string",
            "description": "ISO 8601 datetime string with timezone. MUST be in format: YYYY-MM-DDTHH:MM:SS.000Z (e.g., 2026-02-04T00:00:00.000Z). This filters events occurring after this date."
        }
    },
    "required": ["afterDate"],
    "additionalProperties": False
}

GET_EVENT_BY_SLUG_SCHEMA = {
    "type": "object",
    "properties": {
        "event_slug": {
            "type": "string",
            "description": "The unique slug identifier for the event (e.g., 'new-year-party-2026')"
        }
    },
    "required": ["event_slug"],
    "additionalProperties": False
}

TOOLS = {
    "get_all_events": {
        "description": "Retrieve a paginated list of upcoming events at Big Bull club. Use afterDate parameter to filter events occurring after a specific date. The afterDate MUST be in ISO 8601 format with timezone (e.g., 2026-02-04T00:00:00.000Z).",
        "inputSchema": GET_ALL_EVENTS_SCHEMA,
        "handler": tool_get_all_events,
    },
    "get_event_by_slug": {
        "description": "Retrieve complete details of a specific event using its unique slug identifier. Returns event information including booking types and table availability.",
        "inputSchema": GET_EVENT_BY_SLUG_SCHEMA,
        "handler": tool_get_event_by_slug,
    },
}


def get_tools_list():
    """Get list of all tools with their schemas for MCP protocol"""
    return [
        {
            "name": name,
            "description": tool["description"],
            "inputSchema": tool["inputSchema"]
        }
        for name, tool in TOOLS.items()
    ]


async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name not in TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {name}"
        }
    
    tool = TOOLS[name]
    
    try:
        # Handle get_all_events with defaults
        if name == "get_all_events":
            processed_args = {
                "page": arguments.get("page", 0),
                "size": arguments.get("size", 4),
                "sortBy": arguments.get("sortBy", "eventDateTime"),
                "sortDir": arguments.get("sortDir", "asc"),
                "afterDate": arguments.get("afterDate")
            }
            
            if not processed_args["afterDate"]:
                return {
                    "success": False,
                    "error": "afterDate is required. Please provide a date in ISO 8601 format (e.g., 2026-02-04T00:00:00.000Z)"
                }
            
            return await tool["handler"](processed_args)
        
        # Handle get_event_by_slug
        elif name == "get_event_by_slug":
            if not arguments.get("event_slug"):
                return {
                    "success": False,
                    "error": "event_slug is required"
                }
            
            return await tool["handler"](arguments)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": name
        }
