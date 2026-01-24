import os
from typing import Optional
from pydantic_settings import BaseSettings

class AgentConfig(BaseSettings):
    """Configuration for the AI Agent and MCP Tools"""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Backend API Configuration
    phase_ii_backend_url: str = os.getenv("PHASE_II_BACKEND_URL", "http://localhost:8000")

    # Agent Configuration
    agent_timeout: int = int(os.getenv("AGENT_TIMEOUT", "30"))  # seconds
    max_tool_retries: int = int(os.getenv("MAX_TOOL_RETRIES", "3"))

    # Rate Limiting
    tool_rate_limit_requests: int = int(os.getenv("TOOL_RATE_LIMIT_REQUESTS", "100"))
    tool_rate_limit_window: int = int(os.getenv("TOOL_RATE_LIMIT_WINDOW", "60"))  # seconds

    # Database Configuration (needed to avoid validation error)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

    # Better Auth Configuration
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET", "")
    better_auth_url: str = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

    # Backend API Configuration
    backend_api_url: str = os.getenv("BACKEND_API_URL", "http://localhost:8000/api")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"

# Global configuration instance
config = AgentConfig()