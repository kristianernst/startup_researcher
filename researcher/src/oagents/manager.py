from __future__ import annotations

from agents import Agent

from src.models.model_register import get_model_from_spec, model_registry
from src.setup import settings
from src.types import CompanyFundingSearchResults

__all__ = ["get_manager_agent"]

model = model_registry.get_model(settings.RESEARCH_LM)


MANAGER_INSTRUCTIONS = """
You are a manager agent that is responsible for delivering the final output to the user containing the research findings for a given query.
You are specifically given the task of condensely researching startup firms, particularly related to funding activities.

You have a research agent that you leverage to this, and you plan iteratively calling this agent to gather more information and steering it towards the final output, which you are responsible for delivering.
The final output is a report that will be displayed on a website, so it is important that it is professional and well-formatted.
tone of voice for summary, tech savvy, concise, clear, and storytelling.

When you generate the summary, use markdown formatting to make it more readable.
if multiple companies are mentioned, try not just to list them all, but bucket them meaningfully and tell a narrating story about them.
Each company should be mentioned directly in the summary.
"""


def get_manager_agent(research_agent: Agent) -> Agent:
    """
    Get manager agent, which is responsible for managing the research process.
    """

    return Agent(
        name="ManagerAgent",
        instructions=MANAGER_INSTRUCTIONS,
        handoff_description="Manager agent that is responsible for delivering the final output to the user containing the research findings for a given query.",
        model=get_model_from_spec(model),
        model_settings=model.model_settings,
        tools=[
            research_agent.as_tool(
                tool_name="research_agent",
                tool_description="Research agent that is responsible for researching the given query.",
            )
        ],
        # handoffs=[research_agent],
        output_type=CompanyFundingSearchResults,
    )
