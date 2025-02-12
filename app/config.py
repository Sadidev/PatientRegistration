from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Set

class Settings(BaseSettings):
    # Upload settings
    UPLOAD_DIR: Path = Path("uploads")
    ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png"}
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    TEMPLATE_FOLDER: Path = Path("app/templates")

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

# Create a global settings instance
settings = Settings()