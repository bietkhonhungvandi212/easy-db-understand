"""
Main configuration settings for the Insurance Database Agent
"""
import os
from typing import Optional, List
from pydantic import  Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseSettings(BaseSettings):
    """Database connection settings"""
    host: str = os.getenv("MYSQL_HOST", "localhost")
    port: int = int(os.getenv("MYSQL_PORT", "3306"))
    database: str = os.getenv("MYSQL_DATABASE", "insurance_db")
    user: str = os.getenv("MYSQL_USER", "root")
    password: str = os.getenv("MYSQL_PASSWORD", "")
    charset: str = os.getenv("MYSQL_CHARSET", "utf8mb4")
    url: str = os.getenv("MYSQL_URL", "")

    @property
    def connection_string(self) -> str:
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

class LLMSettings(BaseSettings):
    """LLM API settings"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))


class VectorSettings(BaseSettings):
    """Vector database settings"""
    host: str = os.getenv("VECTOR_HOST", "localhost")
    port: int = int(os.getenv("VECTOR_PORT", "6333"))
    collection: str = os.getenv("VECTOR_COLLECTION", "insurance_vectors")


class AgentSettings(BaseSettings):
    """Agent configuration settings"""
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))
    timeout: int = int(os.getenv("AGENT_TIMEOUT", "300"))


class APISettings(BaseSettings):
    """API server settings"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("API_DEBUG", "False").lower() == "true"


class Settings:
    """Main application settings"""
    database = DatabaseSettings()
    llm = LLMSettings()
    vector = VectorSettings()
    agent = AgentSettings()
    api = APISettings()
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()