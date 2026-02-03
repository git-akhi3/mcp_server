from fastapi import APIRouter, HTTPException
from app.mcp.registry import TOOLS

router = APIRouter(prefix="/mcp")


@router.get("/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": name,
                "description": meta["description"],
            }
            for name, meta in TOOLS.items()
        ]
    }


@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, payload: dict):
    tool = TOOLS.get(tool_name)

    if not tool:
        raise HTTPException(404, "Tool not found")

    result = await tool["handler"](payload)
    return result
