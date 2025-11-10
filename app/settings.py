"""Application settings and configuration."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-minimum-32-characters-required",
        min_length=32
    )
    JWT_EXPIRE_DAYS: int = 1
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # AI Provider (optional)
    AI_PROVIDER: str = "openai"
    AI_BASE_URL: str = ""
    AI_MODEL: str = "tiiuae/falcon-7b-instruct"
    AI_API_KEY: str = ""
    AI_TIMEOUT: int = 30
    AI_MAX_RETRIES: int = 2
    AI_SYSTEM_PROMPT: str = (
        "You are a helpful financial education assistant for users in Bangladesh. "
        "Provide concise, actionable advice. Include formulas and explanations when relevant. "
        "Always remind users this is educational guidance, not professional financial advice. "
        "Use BDT (৳) for currency references."
    )
    
    # Feature Flags
    IS_REGULATED_PARTNER: bool = False
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Defaults for Bangladesh context
    DEFAULT_CURRENCY: str = "BDT"
    DEFAULT_LOCALE: str = "bn_BD"
    DEFAULT_CPI_RATE: float = 7.0  # Annual inflation estimate
    DEFAULT_FUN_RATIO: float = 0.15  # 15% of income for discretionary spending
    MAX_DTI_RATIO: float = 0.4  # 40% debt-to-income max for affordability
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting (in-memory, basic)
    MAX_LOGIN_ATTEMPTS: int = 5
    MAX_AI_REQUESTS_PER_MINUTE: int = 10
    
    # CSV Import
    MAX_CSV_SIZE_MB: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()