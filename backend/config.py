"""Application configuration settings."""

import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
DUPLICATE_WINDOW_SECONDS: int = int(os.getenv("DUPLICATE_WINDOW_SECONDS", "300"))
