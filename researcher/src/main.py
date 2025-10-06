from __future__ import annotations

import asyncio
import logging
import os

import chz
from braintrust import init_logger
from braintrust.wrappers.openai import BraintrustTracingProcessor
from agents import set_trace_processors

from src.setup import settings
from src.flows.research_flow import run_research_flow
from src.oagents.input_parser import parse_input
from src.types import SearchInput
from src.db.digests import insert_digest
from src.logging_config import configure_logging

_LOGGER = logging.getLogger("startup_researcher.main")


@chz.chz
class UserInput:
    q: str = chz.field(default="Hey. retrieve all danish startups getting funding in August 2025.")


os.environ["BRAINTRUST_API_KEY"] = settings.BRAINTRUST_API_KEY

set_trace_processors([BraintrustTracingProcessor(init_logger(settings.BRAINTRUST_PROJECT_NAME))])


async def _async_main(q: str) -> None:
    configure_logging()
    _LOGGER.info("Parsing input")
    _LOGGER.info(f"User input: {q}")
    search_input: SearchInput = parse_input(q)
    _LOGGER.info(f"Parsed input: {search_input}")
    _LOGGER.info(f"Max count: {search_input.max_count}")
    _LOGGER.info("Starting research flow")

    with open("data/reports/oai_deep_research.md", "r") as f:
        oai_deep_research = f.read()

    try:
        _LOGGER.info("Running research flow")
        result = await run_research_flow(search_input, other_research=oai_deep_research)
        if not result or (isinstance(result, str) and result.strip() == ""):
            _LOGGER.warning("Research flow returned empty output")
        else:
            _LOGGER.info("Research flow completed successfully")
        if isinstance(result, str):
            _LOGGER.info("Research flow output characters=%d", len(result))
            preview = result[:500]
            if preview != result:
                _LOGGER.debug("Research flow output preview: %s...", preview)
            else:
                _LOGGER.debug("Research flow output: %s", preview)
        else:
            _LOGGER.info("Research flow output type=%s", type(result))
            _LOGGER.debug("Research flow output repr=%r", result)
    except Exception as exc:
        _LOGGER.exception("Research flow failed: %s", exc)
        raise SystemExit(1) from exc

    _LOGGER.info("Persisting research output to database")

    try:
        run_id = await insert_digest(result)
        _LOGGER.info("Saved research output with run_id=%s", run_id)
    except Exception as exc:
        _LOGGER.exception("Failed to persist research output: %s", exc)
        raise


def main(user_input: UserInput) -> None:
    asyncio.run(_async_main(user_input.q))


if __name__ == "__main__":
    chz.nested_entrypoint(main)
