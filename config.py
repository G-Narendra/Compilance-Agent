"""
config.py
main config file for the agent. loaded from .env
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # nvidia nims api config
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    compliance_model: str = "microsoft/phi-3-mini-128k-instruct"
    use_mock_llm: bool = False

    # vector db (qdrant in-memory)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # api
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # compliance engine
    max_document_size_mb: int = 50
    analysis_timeout_seconds: int = 120
    max_tokens_per_analysis: int = 4096

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    # cache this so we don't spam env reads on every call
    return Settings()
