from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Any, Dict, List, Optional, AsyncGenerator
import json
import uuid
import asyncio

from app.mcp.registry import get_tools_list, call_tool as registry_call_tool, SYSTEM_INSTRUCTIONS

mcp_router = APIRouter()

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "bigbull-events"
SERVER_VERSION = "1.0.0"


def create_mcp_response(result: Any, request_id: Optional[str] = None) -> Dict:
    """Create a properly formatted MCP response envelope"""
    response = {
        "jsonrpc": "2.0",
        "result": result
    }
    if request_id is not None:
        response["id"] = request_id
    return response


def create_mcp_error(code: int, message: str, request_id: Optional[str] = None) -> Dict:
    """Create a properly formatted MCP error response"""
    response = {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        }
    }
    if request_id is not None:
        response["id"] = request_id
    return response


@mcp_router.get("/.well-known/mcp.json")
async def mcp_discovery():
    """
    MCP Discovery endpoint - returns server metadata and available tools.
    ChatGPT uses this to discover the MCP server capabilities.
    """
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


@mcp_router.get("/.well-known/mcp")
async def mcp_discovery_alt():
    return await mcp_discovery()


@mcp_router.get("/mcp")
async def mcp_discovery_root():
    return await mcp_discovery()


@mcp_router.post("/mcp")
async def mcp_handler(request: Request):

    try:
        body = await request.json()
    except json.JSONDecodeError:
        # Return SSE error response
        async def error_stream():
            error_response = create_mcp_error(-32700, "Parse error: Invalid JSON")
            yield f"data: {json.dumps(error_response)}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    # Extract JSON-RPC fields
    jsonrpc = body.get("jsonrpc")
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    # Validate JSON-RPC version
    if jsonrpc != "2.0":
        async def error_stream():
            error_response = create_mcp_error(-32600, "Invalid Request: jsonrpc must be '2.0'", request_id)
            yield f"data: {json.dumps(error_response)}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    # Handle different MCP methods with SSE
    if method == "initialize":
        return await handle_initialize_sse(params, request_id)
    elif method == "tools/list":
        return await handle_tools_list_sse(params, request_id)
    elif method == "tools/call":
        return await handle_tools_call_sse(params, request_id)
    elif method == "ping":
        return await handle_ping_sse(request_id)
    else:
        async def error_stream():
            error_response = create_mcp_error(-32601, f"Method not found: {method}", request_id)
            yield f"data: {json.dumps(error_response)}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )


# SSE Handler Functions
async def handle_initialize_sse(params: Dict, request_id: Optional[str]) -> StreamingResponse:
    """Handle MCP initialize request with SSE"""
    async def event_stream():
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
        yield f"data: {json.dumps(response)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def handle_ping_sse(request_id: Optional[str]) -> StreamingResponse:
    """Handle MCP ping request with SSE"""
    async def event_stream():
        response = create_mcp_response({}, request_id)
        yield f"data: {json.dumps(response)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def handle_tools_list_sse(params: Dict, request_id: Optional[str]) -> StreamingResponse:
    """Handle MCP tools/list request with SSE"""
    async def event_stream():
        result = {
            "tools": get_tools_list()
        }
        response = create_mcp_response(result, request_id)
        yield f"data: {json.dumps(response)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def handle_tools_call_sse(params: Dict, request_id: Optional[str]) -> StreamingResponse:
    """Handle MCP tools/call request with SSE"""
    async def event_stream():
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            error_response = create_mcp_error(-32602, "Invalid params: 'name' is required", request_id)
            yield f"data: {json.dumps(error_response)}\n\n"
            return

        try:
            # Call tool using centralized registry
            tool_result = await registry_call_tool(tool_name, arguments)

            # Format response in MCP content block format
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_result, indent=2, default=str)
                    }
                ],
                "isError": not tool_result.get("success", False)
            }

            response = create_mcp_response(result, request_id)
            yield f"data: {json.dumps(response)}\n\n"

        except Exception as e:
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "success": False,
                            "error": str(e)
                        }, indent=2)
                    }
                ],
                "isError": True
            }
            response = create_mcp_response(result, request_id)
            yield f"data: {json.dumps(response)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@mcp_router.options("/mcp")
async def mcp_options():
    """Handle CORS preflight requests"""
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@mcp_router.options("/.well-known/mcp")
async def mcp_discovery_alt_options():
    """Handle CORS preflight for alternative discovery endpoint"""
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
