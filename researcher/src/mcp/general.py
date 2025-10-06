from dataclasses import dataclass
from typing import Sequence

from agents.mcp import (
    MCPServerSse,
    MCPServerSseParams,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
)
from src.setup import settings
import logging


logger = logging.getLogger("startup_researcher.mcp")


class ConstrainedMCPServerSse(MCPServerSse):
    def __init__(
        self, params: MCPServerSseParams, name: str, allowed_prefixes: Sequence[str], **kwargs
    ):
        super().__init__(params=params, name=name, **kwargs)
        self.allowed_prefixes = tuple(allowed_prefixes)

    async def list_tools(self):
        tools = await super().list_tools()
        return [
            tool for tool in tools if any(tool.name.startswith(p) for p in self.allowed_prefixes)
        ]


class ConstrainedMCPServerHttp(MCPServerStreamableHttp):
    def __init__(
        self,
        params: MCPServerStreamableHttpParams,
        name: str,
        allowed_prefixes: Sequence[str],
        **kwargs,
    ):
        super().__init__(params=params, name=name, **kwargs)
        self.allowed_prefixes = tuple(allowed_prefixes)

    async def list_tools(self):
        tools = await super().list_tools()
        return [
            tool for tool in tools if any(tool.name.startswith(p) for p in self.allowed_prefixes)
        ]


@dataclass(frozen=True)
class MCPDefinition:
    key: str
    display_name: str
    url_setting: str | None  # None for remote servers
    enabled_setting: str
    allowed_tool_prefixes: Sequence[str] | None = None
    server_type: str = "sse"  # "sse" or "http"
    remote_url: str | None = None


MCP_DEFINITIONS: list[MCPDefinition] = [
    # Remote Exa MCP (recommended - no local server needed)
    MCPDefinition(
        key="exa",
        display_name="Exa",
        url_setting=None,
        enabled_setting="ENABLE_EXA_MCP",
        server_type="http",
        remote_url="https://mcp.exa.ai/mcp",
    ),
    # Local/SSE-based Exa (commented out - use remote instead)
    # MCPDefinition(
    #     key="exa_local",
    #     display_name="Exa Local",
    #     url_setting="EXA_MCP_URL",
    #     enabled_setting="ENABLE_EXA_LOCAL_MCP",
    #     server_type="sse",
    # ),
]


class MCPRegistry:
    """Lightweight registry to manage optional MCP servers.

    - Respects ENABLE_* flags from settings
    - Connects only enabled servers
    - Tracks availability and cleans up gracefully
    """

    def __init__(self) -> None:
        self._servers: dict[str, MCPServerSse | MCPServerStreamableHttp] = {}
        self._available: dict[str, bool] = {}

        for d in MCP_DEFINITIONS:
            enabled = bool(getattr(settings, d.enabled_setting, False))
            if not enabled:
                continue

            # Determine URL (remote or from settings)
            if d.remote_url:
                url = d.remote_url
                logger.info(f"Using remote MCP: {d.key} at {url}")
            elif d.url_setting:
                url = str(getattr(settings, d.url_setting, "") or "")
                if not url:
                    logger.warning(f"MCP enabled but URL empty: {d.key} ({d.url_setting})")
                    continue
            else:
                logger.warning(f"MCP definition missing URL: {d.key}")
                continue

            # Create server based on type
            if d.server_type == "http":
                # HTTP-based remote MCP (Exa searches can take 30-60s)
                if d.allowed_tool_prefixes:
                    self._servers[d.key] = ConstrainedMCPServerHttp(
                        MCPServerStreamableHttpParams(url=url, headers={}),
                        name=d.display_name,
                        allowed_prefixes=d.allowed_tool_prefixes,
                        client_session_timeout_seconds=240,
                    )
                else:
                    self._servers[d.key] = MCPServerStreamableHttp(
                        MCPServerStreamableHttpParams(url=url, headers={}),
                        name=d.display_name,
                        client_session_timeout_seconds=240,
                    )
            else:
                # SSE-based local MCP
                if d.allowed_tool_prefixes:
                    self._servers[d.key] = ConstrainedMCPServerSse(
                        MCPServerSseParams(url=url, headers={}),
                        name=d.display_name,
                        allowed_prefixes=d.allowed_tool_prefixes,
                        client_session_timeout_seconds=240,
                    )
                else:
                    self._servers[d.key] = MCPServerSse(
                        MCPServerSseParams(url=url, headers={}),
                        name=d.display_name,
                        client_session_timeout_seconds=240,
                    )

            self._available[d.key] = False

    def enabled_names(self) -> list[str]:
        return list(self._servers.keys())

    def get(self, name: str) -> MCPServerSse | MCPServerStreamableHttp | None:
        return self._servers.get(name)

    def is_available(self, name: str) -> bool:
        return bool(self._available.get(name, False))

    async def connect_enabled(self) -> None:
        """Attempt to connect all enabled servers; do not raise if some fail."""
        for name in self.enabled_names():
            server = self._servers.get(name)
            if not server:
                continue
            try:
                logger.info(f"MCP connecting: {name} ...")
                await server.connect()
                self._available[name] = True
                logger.info(f"MCP connected: {name}")
            except Exception as e:
                self._available[name] = False
                logger.warning(f"MCP unavailable: {name} error={e}")

    async def cleanup_all(self) -> None:
        """Cleanup all servers that were attempted; ignore errors."""
        for name, server in self._servers.items():
            try:
                await server.cleanup()
                logger.info(f"MCP disconnected: {name}")
            except Exception as e:
                logger.warning(f"MCP disconnect failed: {name} error={e}")

    def get_available_servers(self) -> Sequence[MCPServerSse | MCPServerStreamableHttp]:
        return [self._servers[n] for n, ok in self._available.items() if ok]


mcp_registry = MCPRegistry()


__all__ = [
    "mcp_registry",
]
