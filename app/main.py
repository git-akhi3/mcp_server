from fastapi import FastAPI
from app.mcp.server import router as mcp_router

app = FastAPI(
    title="Event MCP Server",
    description="MCP tool server for Event Platform",
)

app.include_router(mcp_router)


@app.get("/")
async def root():
    return {"status": "mcp-server-running"}
