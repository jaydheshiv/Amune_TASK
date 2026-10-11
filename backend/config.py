"""Application configuration settings."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
DUPLICATE_WINDOW_SECONDS: int = int(os.getenv("DUPLICATE_WINDOW_SECONDS", "300"))

# Groq API configuration for AI auto-categorization
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_TIMEOUT_SECONDS: float = float(os.getenv("GROQ_TIMEOUT_SECONDS", "3.0"))
