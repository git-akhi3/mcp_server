from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import traceback

from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)

server = Server("bigbull-events")


# Strict JSON Schema definitions for ChatGPT compatibility
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


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_all_events",
            description="Retrieve a paginated list of upcoming events at Big Bull club. Use afterDate parameter to filter events occurring after a specific date. The afterDate MUST be in ISO 8601 format with timezone (e.g., 2026-02-04T00:00:00.000Z).",
            inputSchema=GET_ALL_EVENTS_SCHEMA,
        ),
        Tool(
            name="get_event_by_slug",
            description="Retrieve complete details of a specific event using its unique slug identifier. Returns event information including booking types and table availability.",
            inputSchema=GET_EVENT_BY_SLUG_SCHEMA,
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        print(f"[MCP] Tool called: {name}")
        print(f"[MCP] Arguments: {json.dumps(arguments, indent=2)}")

        if name == "get_all_events":
            # Apply defaults for optional parameters
            processed_args = {
                "page": arguments.get("page", 0),
                "size": arguments.get("size", 4),
                "sortBy": arguments.get("sortBy", "eventDateTime"),
                "sortDir": arguments.get("sortDir", "asc"),
                "afterDate": arguments.get("afterDate")
            }
            
            # Validate required field
            if not processed_args["afterDate"]:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "afterDate is required. Please provide a date in ISO 8601 format (e.g., 2026-02-04T00:00:00.000Z)"
                    }, indent=2)
                )]
            
            result = await tool_get_all_events(processed_args)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        if name == "get_event_by_slug":
            # Validate required field
            if not arguments.get("event_slug"):
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "event_slug is required"
                    }, indent=2)
                )]
            
            result = await tool_get_event_by_slug(arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        # Unknown tool error
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Unknown tool: {name}"
            }, indent=2)
        )]

    except Exception as e:
        print(f"[MCP] Error in tool {name}: {str(e)}")
        print(f"[MCP] Traceback: {traceback.format_exc()}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "tool": name
            }, indent=2)
        )]
