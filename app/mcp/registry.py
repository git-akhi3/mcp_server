from typing import Dict, Any, List
from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)
from app.mcp.schemas import (
    GET_ALL_EVENTS_SCHEMA,
    GET_EVENT_BY_SLUG_SCHEMA,
)
from constants import ToolName, TOOL_DESCRIPTIONS


# Tools Registry 
TOOLS: Dict[str, Dict[str, Any]] = {
    ToolName.GET_ALL_EVENTS: {
        "description": TOOL_DESCRIPTIONS[ToolName.GET_ALL_EVENTS],
        "inputSchema": GET_ALL_EVENTS_SCHEMA,
        "handler": tool_get_all_events,
    },
    ToolName.GET_EVENT_BY_SLUG: {
        "description": TOOL_DESCRIPTIONS[ToolName.GET_EVENT_BY_SLUG],
        "inputSchema": GET_EVENT_BY_SLUG_SCHEMA,
        "handler": tool_get_event_by_slug,
    },
}


def get_tools_list() -> List[Dict[str, Any]]:
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
        if name == ToolName.GET_ALL_EVENTS:
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
        
        elif name == ToolName.GET_EVENT_BY_SLUG:
            if not arguments.get("event_slug"):
                return {
                    "success": False,
                    "error": "event_slug is required"
                }
            
            return await tool["handler"](arguments)
        
        return await tool["handler"](arguments)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": name
        }
