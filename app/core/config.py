from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Project Settings
    PROJECT_NAME: str

    # Project Admin Settings
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # JWT Auth
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = 'HS256'

    # Data Base
    DATABASE_FILE: str = 'database.db'

    @computed_field
    @property
    def DATABASE_PATH(self) -> Path:
        """Database full path to SQLite file"""
        return Path(__file__).parent.parent / self.DATABASE_FILE

    # API
    API_V1_STR: str = "/api/v1"


settings = Settings()
