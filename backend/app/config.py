from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "dev-secret-change-me"
    frontend_origin: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg2://launchpath:launchpath@localhost:5432/launchpath"

    clerk_jwks_url: str = ""        # e.g. https://<app>.clerk.accounts.dev/.well-known/jwks.json
    clerk_issuer: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    redis_url: str = "redis://localhost:6379/0"

    enabled_adapters: str = "sample"
    serpapi_key: str = ""
    cron_secret: str = ""   # if set, POST /api/discovery/run requires Authorization: Bearer <this>

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "LaunchPath <noreply@launchpath.app>"

    @property
    def adapters(self) -> list[str]:
        return [a.strip() for a in self.enabled_adapters.split(",") if a.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
