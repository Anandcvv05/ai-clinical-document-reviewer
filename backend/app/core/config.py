from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    database_url: str = "sqlite:///./clinical_reviewer.db"
    cors_origins: list[str] = [
    "http://localhost:5173",
    "https://clinicalreview-ai.vercel.app",
]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

settings = Settings()
