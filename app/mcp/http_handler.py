from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Any, Dict, List, Optional, AsyncGenerator
import json
import uuid
import asyncio

from app.tools.event_tools import (
    tool_get_all_events,
    tool_get_event_by_slug,
)

mcp_router = APIRouter()

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "bigbull-events"
SERVER_VERSION = "1.0.0"

GET_ALL_EVENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "page": {
            "type": "integer",
            "description": "Page number for pagination (0-indexed). Default is 0."
        },
        "size": {
            "type": "integer",
            "description": "Number of events per page. Default is 4."
        },
        "sortBy": {
            "type": "string",
            "description": "Field to sort by. Default is 'eventDateTime'."
        },
        "sortDir": {
            "type": "string",
            "description": "Sort direction: 'asc' for ascending, 'desc' for descending.",
            "enum": ["asc", "desc"]
        },
        "afterDate": {
            "type": "string",
            "description": "ISO 8601 datetime string with timezone. Format: YYYY-MM-DDTHH:MM:SS.000Z (e.g., 2026-02-04T00:00:00.000Z). Filters events occurring after this date."
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

TOOLS_DEFINITION = [
    {
        "name": "get_all_events",
        "description": "Retrieve a paginated list of upcoming events at Big Bull club. Use afterDate parameter to filter events occurring after a specific date. The afterDate MUST be in ISO 8601 format with timezone (e.g., 2026-02-04T00:00:00.000Z).",
        "input_schema": GET_ALL_EVENTS_SCHEMA 
    },
    {
        "name": "get_event_by_slug",
        "description": "Retrieve complete details of a specific event using its unique slug identifier. Returns event information including booking types and table availability.",
        "input_schema": GET_EVENT_BY_SLUG_SCHEMA 
    }
]


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
        "tools": TOOLS_DEFINITION
    }
    return JSONResponse(
        content=metadata,
        media_type="application/json"
    )


@mcp_router.get("/.well-known/mcp")
async def mcp_discovery_alt():
    """Alternative discovery endpoint without .json extension"""
    return await mcp_discovery()


@mcp_router.get("/mcp")
async def mcp_discovery_root():
    """Discovery endpoint at /mcp root for clients that check here"""
    return await mcp_discovery()


@mcp_router.post("/mcp")
async def mcp_handler(request: Request):
    """
    Main MCP protocol handler with SSE (Server-Sent Events) support.
    Handles JSON-RPC 2.0 requests for MCP operations over SSE.
    """
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
                "version": SERVER_VERSION
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
            "tools": TOOLS_DEFINITION
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
    async def event_stream():
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            error_response = create_mcp_error(-32602, "Invalid params: 'name' is required", request_id)
            yield f"data: {json.dumps(error_response)}\n\n"
            return

        try:
            if tool_name == "get_all_events":
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
                    result = {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "success": False,
                                    "error": "afterDate is required. Please provide a date in ISO 8601 format (e.g., 2026-02-04T00:00:00.000Z)"
                                }, indent=2)
                            }
                        ],
                        "isError": True
                    }
                    response = create_mcp_response(result, request_id)
                    yield f"data: {json.dumps(response)}\n\n"
                    return

                tool_result = await tool_get_all_events(processed_args)

            elif tool_name == "get_event_by_slug":
                # Validate required field
                if not arguments.get("event_slug"):
                    result = {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "success": False,
                                    "error": "event_slug is required"
                                }, indent=2)
                            }
                        ],
                        "isError": True
                    }
                    response = create_mcp_response(result, request_id)
                    yield f"data: {json.dumps(response)}\n\n"
                    return

                tool_result = await tool_get_event_by_slug(arguments)

            else:
                error_response = create_mcp_error(-32602, f"Unknown tool: {tool_name}", request_id)
                yield f"data: {json.dumps(error_response)}\n\n"
                return

            # Format response in MCP content block format
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_result, indent=2, default=str)
                    }
                ]
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


    """Handle MCP tools/call request"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return JSONResponse(
            content=create_mcp_error(-32602, "Invalid params: 'name' is required", request_id),
            status_code=400,
            media_type="application/json"
        )

    try:
        if tool_name == "get_all_events":
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
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "success": False,
                                "error": "afterDate is required. Please provide a date in ISO 8601 format (e.g., 2026-02-04T00:00:00.000Z)"
                            }, indent=2)
                        }
                    ],
                    "isError": True
                }
                return JSONResponse(
                    content=create_mcp_response(result, request_id),
                    media_type="application/json"
                )

            tool_result = await tool_get_all_events(processed_args)

        elif tool_name == "get_event_by_slug":
            # Validate required field
            if not arguments.get("event_slug"):
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "success": False,
                                "error": "event_slug is required"
                            }, indent=2)
                        }
                    ],
                    "isError": True
                }
                return JSONResponse(
                    content=create_mcp_response(result, request_id),
                    media_type="application/json"
                )

            tool_result = await tool_get_event_by_slug(arguments)

        else:
            return JSONResponse(
                content=create_mcp_error(-32602, f"Unknown tool: {tool_name}", request_id),
                status_code=400,
                media_type="application/json"
            )

        # Format response in MCP content block format
        result = {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(tool_result, indent=2, default=str)
                }
            ]
        }

        return JSONResponse(
            content=create_mcp_response(result, request_id),
            media_type="application/json"
        )

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
        return JSONResponse(
            content=create_mcp_response(result, request_id),
            media_type="application/json"
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
