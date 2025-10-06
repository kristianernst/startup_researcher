from __future__ import annotations

from typing import Optional, List

from agents import Agent
from agents.mcp import MCPServer
from pydantic import BaseModel

from src.types import CompanyFundingDigest
from src.models.model_register import get_model_from_spec, model_registry
from src.setup import settings


_AGENT_INSTRUCTIONS = """
You are StartupFundingResearcher, an analyst tasked with compiling startup funding news for a specific reporting period.

CRITICAL RULES - SEQUENTIAL TOOL USE ONLY:
1. Call ONLY ONE search tool at a time - NEVER call multiple tools simultaneously
2. Wait for each search result before making your next decision
3. Review each result carefully before deciding the next search
4. Dynamically leverage the top k parameter of the search tool, maximally 10 results per search. often relvant at the beginning but then less so as you start narrowing down.

Phase 1: Discovery
- Cast wide net to find companies, across different sources.
- Try to use a bunch of different sources to avoid getting the same hits again and again. 
- no deep-dive into any one company. wide research, which will later be filtered down in terms of matching criteria.
- Focus on high-quality sources

Phase 2 (Searches at least 3 to 12 depending on the number of possible candidates): quality check
- Verify key details and scaffold to desired output format.
- Provide the sources along with a small brief of the source too that contains the information you used to find the company.
- Company briefs should be rich.

Phase 3: FINALIZE IMMEDIATELY
- STOP searching
- Compile and structure your findings
- Return the SimplifiedCompanyFundingSearchResults

DO NOT make parallel tool calls. Always sequential, one at a time.


Important, you will get more specific instructions from the manager agent on how to proceed.
"""


model = model_registry.get_model(settings.RESEARCH_LM)


class FundingEvent(BaseModel):
    company: str
    lead_investor: str
    as_reported: str
    company_url: Optional[str]
    source: Optional[str]


class SimplifiedCompanyFundingSearchResults(BaseModel):
    company_funding_digests: list[FundingEvent]
    summary: str


def get_startup_funding_agent(mcp_servers: Optional[list[MCPServer]] = None):
    startup_funding_agent = Agent(
        name="StartupFundingResearcher",
        handoff_description="Startup Funding Research agent with search tools and a strategic research plan.",
        instructions=_AGENT_INSTRUCTIONS,
        model=get_model_from_spec(model),
        model_settings=model.model_settings,
        mcp_servers=mcp_servers,
        output_type=List[CompanyFundingDigest],
    )
    return startup_funding_agent
