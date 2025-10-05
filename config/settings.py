from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "sqlite:///data/portfolio.db"

    # API Keys
    ETHERSCAN_API_KEY: Optional[str] = None
    POLYGONSCAN_API_KEY: Optional[str] = None
    COINGECKO_API_KEY: Optional[str] = None

    # App Settings
    DEBUG: bool = True
    AUTO_REFRESH_INTERVAL: int = 30
    PRICE_CACHE_TTL: int = 60

    # Rate Limiting
    ETHERSCAN_RATE_LIMIT: int = 5  # calls per second
    COINGECKO_RATE_LIMIT: int = 50  # calls per minute

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
