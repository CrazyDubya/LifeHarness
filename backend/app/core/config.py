from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Union, Any, Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./lifeharness.db"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Token Broker (OpenAI-compatible cheap inference) — question generation
    TOKENBROKER_API_KEY: str = ""
    TOKENBROKER_API_BASE_URL: str = "https://api.thetokenbroker.ai/v1"
    TOKENBROKER_MODEL: str = "gemini-3.8-flash"

    # TypeSafe Jev (decision model) — candidate ranking
    TYPESAFE_API_KEY: str = ""
    TYPESAFE_API_BASE_URL: str = "https://api.typesafe.ai"
    JEV_MODEL: str = "jev-latest"
    JEV_CONFIDENCE_THRESHOLD: float = 0.55

    # Candidate pool
    CANDIDATE_POOL_CAP: int = 25
    CANDIDATES_PER_TOPUP: int = 4
    CANDIDATE_POOL_MIN: int = 5

    # CORS - stored as string in .env, converted to list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"
    
    # Sentry (optional - for error tracking)
    SENTRY_DSN: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def parse_cors_origins(cls, values: Any) -> Any:
        if isinstance(values, dict):
            cors = values.get('CORS_ORIGINS')
            if isinstance(cors, str):
                values['CORS_ORIGINS'] = [origin.strip() for origin in cors.split(',')]
        return values

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
