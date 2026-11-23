"""
DOOM AI — Shared config (breaks circular imports)
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./doom.db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    openrouter_api_key: str = ""
    openrouter_base: str = "https://openrouter.ai/api/v1"
    composio_api_key: str = ""
    composio_base: str = "https://backend.composio.dev/api/v1"
    voice_api_key: str = ""
    pixabay_api_key: str = ""
    pbe_url: str = "http://localhost:8001"
    pbe_dir: str = "../PBE-v5.2.4"
    pbe_port: int = 8001
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/accounts/google/callback"
    resend_api_key: str = ""
    resend_from: str = "DOOM AI <onboarding@resend.dev>"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
