from __future__ import annotations

from typing import Optional

from agents import Agent, ModelSettings, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServer
from pydantic import BaseModel

from src.setup import settings


_AGENT_INSTRUCTIONS = """
You are StartupFundingResearcher, an analyst tasked with compiling startup funding news for a specific reporting period.
Use the available tools to discover recent funding events, double-check investor and amount details, and gather source URLs.
You must use the search tool as far as they are relevant to more or less deeply curate a list of companies and their funding events.
Use the tool one by one and reason about the results, before using it again.
"""


model_settings=ModelSettings(
    temperature=1.0,
    # max_completion_tokens=4000, # needed for Azure gpt5
    reasoning={
        "effort":"low",
        "summary":"auto",
    },
)

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model="azure.gpt-5",
    openai_client=client,
)

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
        instructions=_AGENT_INSTRUCTIONS,
        model=model,
        model_settings=model_settings,
        mcp_servers=mcp_servers,
        output_type=SimplifiedCompanyFundingSearchResults,
    )
    return startup_funding_agent


if __name__ == "__main__":
    import asyncio
    from agents import Runner
    
    async def main():
        
        result = await Runner.run(starting_agent=get_startup_funding_agent(mcp_servers=[]), input="What is the capital of France?")
        print(result)
    
    print("Running agent...")
    asyncio.run(main())