from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rousto:rousto_dev@localhost:5432/rousto"
    api_prefix: str = "/api/v1"
    cors_origins: str = "*"
    dev_user_id: str = "a0000000-0000-4000-8000-000000000001"
    admin_api_key: str = "rousto_admin_dev"
    scan_storage_path: str = "/data/scans"
    ai_provider: str = "stub"
    jwt_secret: str = "rousto_dev_jwt_secret_change_me"
    jwt_access_minutes: int = 60
    jwt_refresh_days: int = 7
    otp_dev_mode: bool = True
    otp_dev_code: str = "123456"


settings = Settings()
