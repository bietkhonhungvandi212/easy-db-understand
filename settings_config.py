"""
Main configuration settings for the Insurance Database Agent
"""
import os
from typing import Optional, List
from pydantic import  Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

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
    base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    api_key: str = os.getenv("LLM_API_KEY", "lm-studio")
    model: str = os.getenv("LLM_MODEL", "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    context_window: int = int(os.getenv("LLM_CONTEXT_WINDOW", "8000"))

class VectorStoreSettings(BaseSettings):
    """Vector store settings"""
    persist_directory: str = os.getenv("VECTOR_STORE_PERSIST_DIRECTORY", "./data/embeddings")
    collection_name: str = os.getenv("VECTOR_STORE_COLLECTION_NAME", "insurance_schema")
    embedding_model: str = os.getenv("VECTOR_STORE_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# class VectorSettings(BaseSettings):
#     """Vector database settings"""
#     host: str = os.getenv("VECTOR_HOST", "localhost")
#     port: int = int(os.getenv("VECTOR_PORT", "6333"))
#     collection: str = os.getenv("VECTOR_COLLECTION", "insurance_vectors")

class AgentSettings(BaseSettings):
    """Agent configuration settings"""
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))
    timeout: int = int(os.getenv("AGENT_TIMEOUT", "300"))

class APISettings(BaseSettings):
    """API server settings"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("API_DEBUG", "False").lower() == "true"

class Settings(BaseSettings):
    """Main settings class that combines all settings"""
    llm: LLMSettings = LLMSettings()
    database: DatabaseSettings = DatabaseSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    agent: AgentSettings = AgentSettings()
    api: APISettings = APISettings()
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

# Create a global settings instance
settings = Settings()