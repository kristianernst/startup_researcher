from __future__ import annotations

from agents.mcp import MCPServerSse, MCPServerSseParams
from src.setup import settings
import os

_DEFAULT_URL = "https://mcp.tavily.com/mcp/?tavilyApiKey="


_HTTP_TIMEOUT = float(os.getenv("MCP_HTTP_TIMEOUT_SECONDS", "5"))
_SSE_READ_TIMEOUT = float(os.getenv("MCP_SSE_READ_TIMEOUT_SECONDS", "60"))

TavilyMCPServerParams = MCPServerSseParams(
    url=_DEFAULT_URL + settings.TAVILY_API_KEY,
    timeout=_HTTP_TIMEOUT,
    sse_read_timeout=_SSE_READ_TIMEOUT,
)

TavilyMCPServer = MCPServerSse(params=TavilyMCPServerParams, name="Tavily")

__all__ = ["TavilyMCPServer"]
