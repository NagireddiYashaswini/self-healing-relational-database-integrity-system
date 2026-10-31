import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "self_healing_test_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_CHARSET: str = "utf8mb4"
    
    APP_ENV: str = "development"
    API_PREFIX: str = "/api"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    DEBUG: bool = True
    
    PROJECT_NAME: str = "Self-Healing Relational Database Integrity System"
    VERSION: str = "2.4.0"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_safe_config(self) -> dict:
        """Returns non-sensitive configuration dictionary for frontend/API consumption."""
        return {
            "db_host": self.DB_HOST,
            "db_port": self.DB_PORT,
            "db_name": self.DB_NAME,
            "db_user": self.DB_USER,
            "db_charset": self.DB_CHARSET,
            "app_env": self.APP_ENV,
            "project_name": self.PROJECT_NAME,
            "version": self.VERSION,
            "frontend_origin": self.FRONTEND_ORIGIN
        }

settings = Settings()
