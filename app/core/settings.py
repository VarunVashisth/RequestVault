# core/settings.py

from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):

    DATABASE_URL : str
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()



