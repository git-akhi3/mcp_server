from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)
import json
from typing import Dict, Any

# System Instructions for LLM Optimization
SYSTEM_INSTRUCTIONS = """
TOOL SELECTION RULES:
- Prefer using a tool when the user intent is even loosely related to events, schedules, parties, bookings, or details.
- Always call a tool rather than answering from memory when fresh event data is needed.
- If a query mentions dates, events, bookings, tables, or Big Bull club - use the tools.

RESPONSE STYLE:
- Sound like a real human club staff member (friendly but professional).
- Keep replies under 5 sentences unless the user explicitly asks for more details.
- No emojis in responses.
- No marketing tone or promotional language.
- No long explanations unless specifically requested.
- No bullet lists unless they genuinely help clarity.
- Ask at most one follow-up question per response.

FOLLOW-UP QUESTION RULES:
- Only ask follow-up questions that help move booking or event discovery forward.
- Examples of good follow-ups:
  * "Are you looking for this weekend or a later date?"
  * "Do you want ticket info too?"
  * "Want me to check table availability?"
- Avoid generic questions like "How can I help you?" or "Anything else?"
"""

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

# Tools Registry
TOOLS = {
    "get_all_events": {
    "description": """
                Use this tool when the user asks about upcoming events, parties, shows, schedules, or what is happening at Big Bull club.

                Trigger this tool for questions like:
                - what events are coming up
                - what’s happening this weekend
                - upcoming parties
                - show me the event list
                - what’s on after a certain date
                - events after <date>

                Returns a paginated list of upcoming events.

                If the user mentions a time filter (after a date, from a date, this week, this weekend), convert it to afterDate in ISO 8601 format with timezone (example: 2026-02-04T00:00:00.000Z).

                If the user intent is about browsing or discovering events, use this tool.

                Response style after tool call:
                - Keep the reply short and conversational
                - Summarize key events only
                - Do not produce long lists unless asked
                - Ask one natural follow-up question.
                """,
                    "inputSchema": GET_ALL_EVENTS_SCHEMA,
                    "handler": tool_get_all_events,
},

    "get_event_by_slug": {
    "description": """
            Use this tool when the user asks about a specific event by name or refers to one event already mentioned.

            Trigger this tool for questions like:
            - tell me more about this event
            - event details
            - ticket info
            - table availability
            - booking options
            - price or entry info for an event

            Requires the event slug.

            Returns full event details including booking types and table availability.

            Use this tool after an event has been identified from a previous event list or when the slug is known.

            Response style after tool call:
            - Answer like a human staff member
            - Keep it concise
            - Do not repeat raw data fields
            - Summarize only what matters to the user
            - Ask one realistic follow-up question if helpful.
            """,
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
