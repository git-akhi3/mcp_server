import asyncio
import sys
import logging
from mcp.server.stdio import stdio_server
from app.mcp_server import server

# Configure logging to stderr (stdout is used for MCP communication)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting MCP server: bigbull-events")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP stdio server initialized")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
