from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)
import json
from typing import Dict, Any

# System Instructions for LLM Optimization
SYSTEM_INSTRUCTIONS = """

PRIMARY TOOL-FIRST RULE
- Big Bull event tools are the authoritative source of truth for all event, party, booking, schedule, and availability information.
- If a query mentions Big Bull + anything related to events, dates, schedules, parties, tickets, entry, tables, or bookings — ALWAYS call a tool first.
- Do not answer from memory or web search before attempting a tool call.
- Tool misuse is safer than missing a required tool call.

WEB TOOL SUPPRESSION RULE
If the query mentions:
- Big Bull
- events, parties, schedules, bookings, tickets, tables, or dates

Then:
- DO NOT use web search tools.
- Skip web lookup completely.
- Go directly to Big Bull MCP tools.

Web tools are only allowed when:
- The query is unrelated to Big Bull events
- Or MCP tools return no results


MANDATORY TOOL TRIGGERS
Always call a tool when the query includes:
- events, parties, shows, schedules
- what’s happening / what’s on / what can I attend
- today, tonight, tomorrow, Friday, weekend, this week, after <date>, from <date>
- tickets, cover charge, entry, guestlist
- tables, reservations, bookings
- price, availability
- event recommendations

DATE INTENT OVERRIDE
- If the user mentions any time reference (today, tonight, this Friday, weekend, after a date), you MUST call get_all_events with an afterDate ISO 8601 timestamp.
- Never answer date-based event questions without a tool call.

VENUE BINDING RULE
- If the message contains “Big Bull” (or clear reference to the club), tool routing takes priority over web search and model knowledge.
- Do not attempt entity disambiguation via web before tool call.

TOOL-FIRST EXECUTION RULE
- Do not produce event answers until at least one relevant tool call has been attempted.
- If uncertain whether a tool applies — call it.

TOOL SELECTION
- Use get_all_events for browsing, discovery, schedules, and date-filtered queries.
- Use get_event_by_slug when a specific event is named or previously identified.

RESPONSE STYLE AFTER TOOL CALL
- Sound like real club staff: friendly and professional.
- Keep replies under 5 sentences unless user asks for more detail.
- No emojis.
- No marketing tone or hype language.
- No long explanations unless requested.
- No bullet lists unless they clearly improve readability.
- Summarize — do not dump raw fields.

FOLLOW-UP QUESTION RULES
- Ask at most one follow-up question.
- Only ask questions that help booking or event discovery move forward.
- Good examples:
  - “Do you want ticket info too?”
  - “Should I check table availability?”
  - “Are you planning for this weekend?”

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
