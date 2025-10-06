from __future__ import annotations

from agents import Agent

from src.models.model_register import get_model_from_spec, model_registry
from src.setup import settings
from src.types import CompanyFundingSearchResults

__all__ = ["get_condense_agent"]

model = model_registry.get_model(settings.RESEARCH_LM)


CONDENSE_INSTRUCTIONS = """
You are specifically given the task of condensely researching startup firms, particularly related to funding activities.
You will be given present research and other research, both of which are important and must be combined into a single report.
No company should occur more than once in the final report.
You will also be given a report format, which you must follow.
The final output is a report that will be displayed on a website, so it is important that it is professional and well-formatted.
tone of voice for summary: george hotz style.
The summary should be rich and engaging.
"""


def get_condense_agent() -> Agent:
    """
    Get condense agent, which is responsible for condensing the research process.
    """
    # set parallel tool calls to none, when no tools are provided
    model_settings = model.model_settings
    model_settings.parallel_tool_calls = None
    return Agent(
        name="CondenseAgent",
        instructions=CONDENSE_INSTRUCTIONS,
        model=get_model_from_spec(model),
        model_settings=model_settings,
        output_type=CompanyFundingSearchResults,
    )
