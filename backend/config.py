"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
TC260 Security Enhanced.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Application Security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    environment: str = "development"
    debug: bool = False
    
    # Security Settings (TC260 Compliance)
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100
    enable_cors: bool = True
    enable_audit_logging: bool = True
    enable_pii_encryption: bool = True
    
    # TLS/SSL
    enforce_https: bool = True
    tls_min_version: str = "1.2"
    
    # API Configuration
    api_title: str = "Council of AI API"
    api_version: str = "1.0.0"
    api_description: str = "AI Safety Verification Platform (TC260 Compliant)"
    
    # CORS (Strict by default)
    cors_origins: list[str] = [
        "https://councilof.ai",
        "https://www.councilof.ai",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ]
    
    # LLM API Keys (optional for Day 1)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    
    # ProofOf.AI Integration (Blockchain Audit Trail)
    proofof_ai_api_key: str | None = None
    proofof_ai_api_url: str = "https://api.proofof.ai"
    enable_blockchain_logging: bool = True
    
    # Data Retention (GDPR/CCPA Compliance)
    data_retention_days: int = 365
    auto_delete_stale_users: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
