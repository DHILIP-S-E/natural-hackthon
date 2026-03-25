"""AURA Configuration — Pydantic Settings with Supabase support."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AURA"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # JWT (use Supabase JWT secret for consistency)
    JWT_SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Storage (MinIO / S3-compatible — Supabase Storage)
    STORAGE_BACKEND: str = "minio"  # "minio", "s3", "supabase"
    STORAGE_ENDPOINT: str = ""  # MinIO endpoint e.g. "168.144.16.134:9000"
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""
    STORAGE_BUCKET: str = "aura-uploads"
    STORAGE_REGION: str = "ap-south-1"
    STORAGE_USE_SSL: bool = False

    # AI Provider: "openai" or "gemini"
    AI_PROVIDER: str = "gemini"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # OpenWeatherMap (optional — Open-Meteo used as free fallback)
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # SMTP Email (works with Gmail, Outlook, any SMTP server)
    SMTP_HOST: str = ""           # e.g. "smtp.gmail.com"
    SMTP_PORT: int = 587          # 587 for TLS, 465 for SSL
    SMTP_USER: str = ""           # e.g. "your-email@gmail.com"
    SMTP_PASSWORD: str = ""       # App password (not your login password)
    SMTP_USE_TLS: bool = True     # True for port 587, False for port 465
    SMTP_FROM_NAME: str = "AURA Beauty"
    SMTP_FROM_EMAIL: str = ""     # defaults to SMTP_USER if empty

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
