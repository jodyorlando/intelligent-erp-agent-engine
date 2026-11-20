import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #application meta
    PROJECT_NAME: str = "Intelligent ERP Agent Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database Setup
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@erp_postgres_db:5432/erp_db?ssl=disable"

    # Redis
    REDIS_URL: str = "redis://erp_redis:6379/0"

    #OpenAI
    OPENAI_API_KEY: str = "mock-key-for-dev"

    #security
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            # Railway generates postgres:// or postgresql:// without the driver prefix
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().strip('"').strip("'")
            if not v.startswith(("redis://", "rediss://", "unix://")):
                return f"redis://{v}"
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings() 