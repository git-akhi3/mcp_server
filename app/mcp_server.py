from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import traceback

from app.mcp.registry import get_tools_list, call_tool as registry_call_tool

server = Server("bigbull-events")


@server.list_tools()
async def list_tools():
    """List all available tools from registry"""
    tools_list = get_tools_list()
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["input_schema"],
        )
        for tool in tools_list
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Call a tool using the centralized registry"""
    try:
        print(f"[MCP] Tool called: {name}")
        print(f"[MCP] Arguments: {json.dumps(arguments, indent=2)}")

        result = await registry_call_tool(name, arguments)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
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
