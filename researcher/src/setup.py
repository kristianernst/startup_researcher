from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_BASE_URL: str
    OPENAI_API_KEY: str

    LLAMACPP_BASE_URL: Optional[str]

    PARSE_LM: str
    RESEARCH_LM: str

    BRAINTRUST_PROJECT_NAME: str
    BRAINTRUST_API_KEY: str

    ENABLE_EXA_MCP: bool
    EXA_MCP_URL: str
    EXA_API_KEY: str

    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
