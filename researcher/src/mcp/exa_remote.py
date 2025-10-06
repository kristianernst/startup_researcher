"""
Exa Remote MCP Server Configuration
Uses Exa's hosted MCP at https://mcp.exa.ai/mcp
"""

from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
import logging

from src.logging_config import configure_logging

logger = logging.getLogger("startup_researcher.exa_remote")


def get_exa_remote_mcp() -> MCPServerStreamableHttp:
    """
    Get Exa's remote MCP server (HTTP-based)

    Benefits:
    - No local server to manage
    - Always up-to-date
    - Includes deep_researcher and other advanced tools

    Docs: https://docs.exa.ai/reference/exa-mcp
    """
    server = MCPServerStreamableHttp(
        MCPServerStreamableHttpParams(url="https://mcp.exa.ai/mcp", headers={}),
        name="Exa",
        client_session_timeout_seconds=120,
    )

    logger.info("Using Exa remote MCP at https://mcp.exa.ai/mcp")
    return server


async def test_exa_remote():
    """Test connection to Exa remote MCP"""
    server = get_exa_remote_mcp()

    try:
        logger.info("Connecting to Exa remote MCP...")
        await server.connect()

        logger.info("Listing available tools...")
        tools = await server.list_tools()

        if tools:
            logger.info("Available Exa MCP tools: %d", len(tools))
            for tool in tools:
                logger.info("Tool %s: %s", tool.name, tool.description[:80])
        else:
            logger.warning("No tools reported by Exa MCP")

        logger.info("✓ Connection successful")

    finally:
        await server.cleanup()


if __name__ == "__main__":
    import asyncio

    configure_logging()
    asyncio.run(test_exa_remote())
