from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rousto:rousto_dev@localhost:5432/rousto"
    api_prefix: str = "/api/v1"
    cors_origins: str = "*"
    dev_user_id: str = "a0000000-0000-4000-8000-000000000001"
    admin_api_key: str = "rousto_admin_dev"


settings = Settings()
