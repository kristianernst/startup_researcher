from dataclasses import dataclass
from typing import Sequence

from agents.mcp import MCPServerSse, MCPServerSseParams
from src.setup import settings
import logging
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("startup_researcher.mcp")


class ConstrainedMCPServer(MCPServerSse):
    def __init__(self, params: MCPServerSseParams, name: str, allowed_prefixes: Sequence[str], **kwargs):
        super().__init__(params=params, name=name, **kwargs)
        self.allowed_prefixes = tuple(allowed_prefixes)

    async def list_tools(self):
        tools = await super().list_tools()
        return [tool for tool in tools if any(tool.name.startswith(p) for p in self.allowed_prefixes)]


@dataclass(frozen=True)
class MCPDefinition:
    key: str
    display_name: str
    url_setting: str
    enabled_setting: str
    allowed_tool_prefixes: Sequence[str] | None = None


MCP_DEFINITIONS: list[MCPDefinition] = [
    MCPDefinition(
        key="exa",
        display_name="Exa",
        url_setting="EXA_MCP_URL",
        enabled_setting="ENABLE_EXA_MCP",
    ),
]


class MCPRegistry:
    """Lightweight registry to manage optional MCP servers.

    - Respects ENABLE_* flags from settings
    - Connects only enabled servers
    - Tracks availability and cleans up gracefully
    """

    def __init__(self) -> None:
        self._servers: dict[str, MCPServerSse] = {}
        self._available: dict[str, bool] = {}

        for d in MCP_DEFINITIONS:
            enabled = bool(getattr(settings, d.enabled_setting, False))
            url = str(getattr(settings, d.url_setting, "") or "")
            if not enabled:
                continue
            if not url:
                logger.warning(f"MCP enabled but URL empty: {d.key} ({d.url_setting})")
                continue
            if d.allowed_tool_prefixes:
                self._servers[d.key] = ConstrainedMCPServer(
                    MCPServerSseParams(url=url, headers={}),
                    name=d.display_name,
                    allowed_prefixes=d.allowed_tool_prefixes,
                    client_session_timeout_seconds=15,
                )
            else:
                self._servers[d.key] = MCPServerSse(
                    MCPServerSseParams(url=url, headers={}),
                    name=d.display_name,
                    client_session_timeout_seconds=15,
                )
            self._available[d.key] = False

    def enabled_names(self) -> list[str]:
        return list(self._servers.keys())

    def get(self, name: str) -> MCPServerSse | None:
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

    def get_available_servers(self) -> Sequence[MCPServerSse]:
        return [self._servers[n] for n, ok in self._available.items() if ok]


mcp_registry = MCPRegistry()


__all__ = [
    "mcp_registry",
]
