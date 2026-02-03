from mcp.server import Server
from mcp.types import Tool

from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)

server = Server("bigbull-events")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_all_events",
            description="Get available events at Big Bull club",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer"},
                    "size": {"type": "integer"},
                    "sortBy": {"type": "string"},
                    "sortDir": {"type": "string"},
                    "afterDate": {"type": "string"}
                },
                "required": ["afterDate"]
            },
        ),
        Tool(
            name="get_event_by_slug",
            description="Get event details by slug",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_slug": {"type": "string"}
                },
                "required": ["event_slug"]
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):

    if name == "get_all_events":
        return await tool_get_all_events(arguments)

    if name == "get_event_by_slug":
        return await tool_get_event_by_slug(arguments)

    raise ValueError("Unknown tool")
