from __future__ import annotations

import argparse, asyncio, logging, os
from typing import Sequence

from braintrust import init_logger
from braintrust.wrappers.openai import BraintrustTracingProcessor
from agents import set_trace_processors

from src.setup import settings
from src.flows.research_flow import run_research_flow
from src.types import Criterion, Search

_LOGGER = logging.getLogger("startup_researcher.main")


def _configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _build_search(args: argparse.Namespace) -> Search:
    criteria: Sequence[Criterion] = [Criterion(description=c) for c in args.criteria]
    return Search(
        query=args.query,
        criteria=list(criteria),
        relevant_count=args.relevant_count,
        max_count=args.max_count,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the startup funding research flow")
    parser.add_argument(
        "--query",
        default="List of companies in copenhagen getting funding in August 2025",
        help="Primary search query passed to the agent",
    )
    parser.add_argument(
        "--criteria",
        nargs="+",
        default=["Funding rounds announced in August 2025", "Copenhagen based startups"],
        help="One or more textual criteria that describe the desired results",
    )
    parser.add_argument(
        "--relevant-count",
        type=int,
        default=5,
        help="Target number of high-quality results the agent should return",
    )
    parser.add_argument(
        "--max-count",
        type=int,
        default=15,
        help="Maximum attempts the agent can make while searching",
    )
    return parser.parse_args()


os.environ["BRAINTRUST_API_KEY"] = settings.BRAINTRUST_API_KEY

set_trace_processors([BraintrustTracingProcessor(init_logger(settings.BRAINTRUST_PROJECT_NAME))])

async def _async_main() -> None:
    _configure_logging()
    args = _parse_args()
    _LOGGER.debug("Parsed args: query='%s', criteria_count=%d, relevant_count=%d, max_count=%d", args.query, len(args.criteria), args.relevant_count, args.max_count)
    search = _build_search(args)
    _LOGGER.info("Starting research flow")

    try:
        _LOGGER.info("Running research flow")
        result = await run_research_flow(search)
        if not result or (isinstance(result, str) and result.strip() == ""):
            _LOGGER.warning("Research flow returned empty output")
        else:
            _LOGGER.info("Research flow completed successfully")
        print(result)
    except Exception as exc:
        _LOGGER.exception("Research flow failed: %s", exc)
        print(exc)
        raise SystemExit(1) from exc


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
