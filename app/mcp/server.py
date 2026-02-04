from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.mcp.registry import TOOLS

router = APIRouter(prefix="/mcp")


class ToolCallRequest(BaseModel):
    arguments: Optional[Dict[str, Any]] = None


@router.get("/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": name,
                "description": meta["description"],
                "inputSchema": meta["inputSchema"]
            }
            for name, meta in TOOLS.items()
        ]
    }


@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, payload: ToolCallRequest):
    tool = TOOLS.get(tool_name)

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    try:
        arguments = payload.arguments or {}
        result = await tool["handler"](arguments)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
