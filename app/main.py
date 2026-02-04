from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.mcp.server import router as mcp_router
from app.mcp.http_handler import mcp_router as mcp_http_router

app = FastAPI(
    title="Event MCP Server",
    description="MCP tool server for Event Platform - ChatGPT Compatible",
)

# CORS middleware for ChatGPT compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(mcp_router)
app.include_router(mcp_http_router)


@app.get("/")
async def root():
    return {"status": "mcp-server-running", "protocol": "MCP 2024-11-05"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
