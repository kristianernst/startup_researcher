from __future__ import annotations

from typing import Optional

from agents import Agent
from agents.mcp import MCPServer

from .startup_funding_agent import get_startup_funding_agent
from .manager import get_manager_agent
from .condense_agent import get_condense_agent
from .input_parser import parse_input


def get_agents(mcp_servers: Optional[list[MCPServer]] = None) -> tuple[Agent, Agent, Agent]:
    """Yields the agents necessary for the research flow"""
    research_agent = get_startup_funding_agent(mcp_servers=mcp_servers)
    manager_agent = get_manager_agent(research_agent=research_agent)
    condense_agent = get_condense_agent()

    return research_agent, manager_agent, condense_agent


__all__ = ["get_startup_funding_agent", "get_manager_agent", "parse_input", "get_agents"]
