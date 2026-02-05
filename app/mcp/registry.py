from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)
import json
from typing import Dict, Any

# System Instructions for LLM Optimization
SYSTEM_INSTRUCTIONS = """
⚠️ CRITICAL: TOOLS ARE MANDATORY - WEB SEARCH IS FORBIDDEN ⚠️

PRIMARY DIRECTIVE - TOOL ENFORCEMENT:
You DO NOT have information about Big Bull events in your training data.
The ONLY way to get Big Bull event information is by calling the provided MCP tools.
Web search is DISABLED and PROHIBITED for all Big Bull queries.

ABSOLUTE RULE:
If user query contains "Big Bull" AND any of these keywords:
- events, parties, shows, schedule, calendar
- what's happening, what's on, upcoming
- tonight, today, tomorrow, weekend, this week
- tickets, bookings, tables, reservations, entry

Then you MUST:
1. IMMEDIATELY call get_all_events tool (with afterDate parameter)
2. Wait for tool response
3. ONLY THEN provide answer based on tool data

You CANNOT:
- Answer without calling the tool first
- Use web search as an alternative
- Use your training data or general knowledge
- Say "let me search" and then use web instead of tools

EXAMPLE - CORRECT BEHAVIOR:
User: "what events at big bull"
Action: Call get_all_events(afterDate="2026-02-04T00:00:00.000Z")
Wait for response, then answer.

EXAMPLE - WRONG BEHAVIOR (FORBIDDEN):
User: "what events at big bull"
Action: Search web → WRONG! Use tool instead!
Action: Answer from memory → WRONG! You have no memory of this!

MANDATORY TOOL TRIGGERS:
These phrases REQUIRE immediate tool call:
- "events at big bull"
- "what's happening at big bull"
- "big bull parties"
- "big bull tonight"
- "big bull this weekend"
- "upcoming events"
- "what's on at big bull"

DATE HANDLING:
- ALWAYS include afterDate in ISO 8601 format: YYYY-MM-DDTHH:MM:SS.000Z
- Current date: 2026-02-04
- "tonight" → "2026-02-04T00:00:00.000Z"
- "this weekend" → "2026-02-04T00:00:00.000Z"
- No afterDate → Use current date

TOOL SELECTION:
- Use get_all_events for: browsing, discovery, schedules, date-filtered queries
- Use get_event_by_slug for: specific event details when slug is known

RESPONSE STYLE (after tool call):
- Sound like club staff: friendly and professional
- Keep replies under 5 sentences unless asked for more
- No emojis, no hype language, no long explanations
- Summarize key info only
- Ask ONE follow-up question if helpful:
  * "Want ticket info?"
  * "Should I check table availability?"
  * "Planning for this weekend?"

REMEMBER: Tool call is NOT optional. It is REQUIRED for all Big Bull event queries.
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

This tool MUST be called for ANY query about Big Bull events. Do NOT use web search instead.

Trigger this tool for questions like:
- what events are coming up
- what's happening this weekend
- upcoming parties
- show me the event list
- what's on after a certain date
- events after <date>
- events at big bull

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
