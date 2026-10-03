from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Union, Any, Optional

DEV_SECRET_KEY = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./lifeharness.db"

    # JWT
    SECRET_KEY: str = DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Vultr API
    VULTR_API_KEY: str = ""
    VULTR_API_BASE_URL: str = "https://api.vultrinference.com/v1"
    VULTR_MODEL: str = "llama2-13b-chat-Q5_K_M"

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

    @model_validator(mode='after')
    def refuse_dev_secret_in_production(self):
        if (
            self.ENVIRONMENT == "production"
            and self.SECRET_KEY == DEV_SECRET_KEY
        ):
            raise ValueError(
                "Refusing to start in production with the default dev SECRET_KEY. "
                "Set a unique SECRET_KEY in the environment."
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
