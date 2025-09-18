from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents import Runner
import logging

from src.oagents import get_startup_funding_agent
from src.mcp.general import mcp_registry
from src.types import Search

@dataclass(slots=True)
class ResearchContext:
    search: Search
    metadata: dict[str, Any] = field(default_factory=dict)


def _search_to_agent_input(search: Search) -> str:
    criteria_string = "\n".join([c.description for c in search.criteria])  if  len(search.criteria) > 0 else ""
    return f"{search.query}\n{criteria_string}"


async def run_research_flow(
    search: Search,
) -> str:
    logger = logging.getLogger("startup_researcher.research_flow")
    context = ResearchContext(search=search)
    
    agent_input = _search_to_agent_input(search)
    logger.debug("Agent input generated (len=%d)", len(agent_input))
    
    logger.info("Connecting enabled MCP servers via registry ...")
    await mcp_registry.connect_enabled()
    mcp_servers = list(mcp_registry.get_available_servers())
    logger.info("MCP servers available: %s", ", ".join(getattr(s, "name", "?") for s in mcp_servers) or "none")


    try:
        logger.info("Running agent with %d MCP server(s)", len(mcp_servers))
        response = await Runner.run(
            starting_agent=get_startup_funding_agent(mcp_servers=mcp_servers),
            input=agent_input,
            context=context,
        )
        logger.debug("Agent run completed")
    finally:
        await mcp_registry.cleanup_all()

    output = response.final_output or ""
    return output


__all__ = ["run_research_flow", "ResearchContext"]
