from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    TAVILY_API_KEY: str
    OPENAI_BASE_URL: str
    OPENAI_API_KEY: str

    BRAINTRUST_PROJECT_NAME: str
    BRAINTRUST_API_KEY: str
    EXA_MCP_URL: str
    ENABLE_EXA_MCP: bool

    class Config:
        env_file = ".env"

settings = Settings()