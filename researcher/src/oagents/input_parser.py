import logging

from openai import OpenAI

from src.types import SearchInput
from src.setup import settings

logger = logging.getLogger("startup_researcher.input_parser")

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)


_PARSE_INSTRUCTIONS = """
You are an input parser for a startup funding research flow.
You are given a user input and you need to parse it into a SearchInput object.
This object is used to guide the search agents later on in the process.
"""


def parse_input(input: str) -> SearchInput:
    try:
        response = client.chat.completions.parse(
            model=settings.PARSE_LM,
            messages=[
                {"role": "system", "content": _PARSE_INSTRUCTIONS},
                {"role": "user", "content": input},
            ],
            response_format=SearchInput,
        )
    except Exception as exc:
        logger.exception("Error parsing input: %s", exc)
        raise

    return response.choices[0].message.parsed
