from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any
import json
from app.mcp.core.protocol import create_mcp_error



async def create_sse_response(data: Dict[str, Any]) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps(data)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def create_sse_error(code: int, message: str, request_id: Any = None) -> StreamingResponse:
    error_response = create_mcp_error(code, message, request_id)
    return await create_sse_response(error_response)