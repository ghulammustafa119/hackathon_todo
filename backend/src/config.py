"""
Configuration module for the backend application.

This module provides centralized configuration for the entire backend,
including JWT settings, database settings, and other application-wide
configuration values.
"""

import os

# JWT Configuration (same as in auth.py)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# Backend API Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api")

# Better Auth Configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Phase II Backend URL
PHASE_II_BACKEND_URL = os.getenv("PHASE_II_BACKEND_URL", "http://localhost:8000")

# Agent Configuration
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "30"))  # seconds
MAX_TOOL_RETRIES = int(os.getenv("MAX_TOOL_RETRIES", "3"))

# Rate Limiting
TOOL_RATE_LIMIT_REQUESTS = int(os.getenv("TOOL_RATE_LIMIT_REQUESTS", "100"))
TOOL_RATE_LIMIT_WINDOW = int(os.getenv("TOOL_RATE_LIMIT_WINDOW", "60"))  # seconds