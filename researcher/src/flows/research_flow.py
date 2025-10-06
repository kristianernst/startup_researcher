from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from agents import Runner
import logging

from src.oagents import get_agents
from src.mcp import mcp_registry
from src.types import SearchInput


@dataclass(slots=True)
class ResearchContext:
    search: SearchInput
    metadata: dict[str, Any] = field(default_factory=dict)


def _search_to_agent_input(search: SearchInput) -> str:
    criteria_string = (
        "\n".join([c.description for c in search.criteria]) if len(search.criteria) > 0 else ""
    )
    return f"{search.query}\n{criteria_string}"


async def run_research_flow(
    search: SearchInput,
    other_research: Optional[str] = None,
) -> str:
    """
    Responsible for the research flow primarily via the manager agent,
    if the user has provided additional context, we also feed this and
    triangulate different knowledge sources
    """

    logger = logging.getLogger("startup_researcher.research_flow")
    context = ResearchContext(search=search)

    agent_input = _search_to_agent_input(search)
    logger.debug("Agent input generated (len=%d)", len(agent_input))

    logger.info("Connecting enabled MCP servers via registry ...")

    await mcp_registry.connect_enabled()
    mcp_servers = list(mcp_registry.get_available_servers())
    logger.info(
        "MCP servers available: %s",
        ", ".join(getattr(s, "name", "?") for s in mcp_servers) or "none",
    )

    try:
        logger.info("Running agent with %d MCP server(s)", len(mcp_servers))

        _, manager_agent, condense_agent = get_agents(mcp_servers=mcp_servers)

        response = await Runner.run(
            starting_agent=manager_agent,
            input=agent_input,
            context=context,
            max_turns=50,
        )

        if other_research:
            response_str = f"""
            <present research>
            {response.final_output.model_dump_json()}
            </present_research>
            <other_research>
            {other_research}
            </other_research>
            """
            response = await Runner.run(
                starting_agent=condense_agent,
                input=response_str,
                context=context,
                max_turns=10,
            )

        logger.debug("Agent run completed")
    finally:
        await mcp_registry.cleanup_all()

    output = response.final_output or ""
    return output


__all__ = ["run_research_flow", "ResearchContext"]
