from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict
import json

from constants import (
    SYSTEM_INSTRUCTIONS,
    MCP_PROTOCOL_VERSION,
    SERVER_NAME,
    SERVER_VERSION,
)
from app.mcp.registry import get_tools_list, call_tool as registry_call_tool
from app.mcp.core.protocol import (
    create_mcp_response,
    create_mcp_error,
    create_content_block,
)
from app.mcp.core.sse import create_sse_response, create_sse_error

mcp_router = APIRouter()

@mcp_router.get("/.well-known/mcp.json")
async def mcp_discovery():
    metadata = {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "protocol_version": MCP_PROTOCOL_VERSION,
        "description": "MCP server for Big Bull club events - fetch upcoming events and event details",
        "instructions": SYSTEM_INSTRUCTIONS,
        "tools": get_tools_list()
    }
    return JSONResponse(
        content=metadata,
        media_type="application/json"
    )

@mcp_router.get("/mcp")
async def mcp_discovery_root():
    return await mcp_discovery()


@mcp_router.post("/mcp")
async def mcp_handler(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return await create_sse_error(-32700, "Parse error: Invalid JSON")

    jsonrpc = body.get("jsonrpc")
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    if jsonrpc != "2.0":
        return await create_sse_error(
            -32600,
            "Invalid Request: jsonrpc must be '2.0'",
            request_id
        )

    if method == "initialize":
        return await handle_initialize(params, request_id)
    elif method == "tools/list":
        return await handle_tools_list(params, request_id)
    elif method == "tools/call":
        return await handle_tools_call(params, request_id)
    elif method == "ping":
        return await handle_ping(request_id)
    else:
        return await create_sse_error(
            -32601,
            f"Method not found: {method}",
            request_id
        )


async def handle_initialize(params: Dict, request_id: str) -> StreamingResponse:
    result = {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "instructions": SYSTEM_INSTRUCTIONS
        }
    }
    response = create_mcp_response(result, request_id)
    return await create_sse_response(response)


async def handle_ping(request_id: str) -> StreamingResponse:
    """Handle MCP ping request"""
    response = create_mcp_response({}, request_id)
    return await create_sse_response(response)


async def handle_tools_list(params: Dict, request_id: str) -> StreamingResponse:
    """Handle MCP tools/list request"""
    result = {
        "tools": get_tools_list()
    }
    response = create_mcp_response(result, request_id)
    return await create_sse_response(response)


async def handle_tools_call(params: Dict, request_id: str) -> StreamingResponse:
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return await create_sse_error(
            -32602,
            "Invalid params: 'name' is required",
            request_id
        )

    try:
        tool_result = await registry_call_tool(tool_name, arguments)
        result = create_content_block(
            tool_result,
            is_error=not tool_result.get("success", False)
        )

        response = create_mcp_response(result, request_id)
        return await create_sse_response(response)

    except Exception as e:
        result = create_content_block(
            {"success": False, "error": str(e)},
            is_error=True
        )
        response = create_mcp_response(result, request_id)
        return await create_sse_response(response)



@mcp_router.options("/mcp")
async def mcp_options():
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@mcp_router.options("/.well-known/mcp")
async def mcp_discovery_options():
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
