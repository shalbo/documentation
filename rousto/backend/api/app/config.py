from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql://rousto:rousto_dev@localhost:5432/rousto"
    api_prefix: str = "/api/v1"
    cors_origins: str = "*"
    admin_api_key: str = "rousto_admin_dev"
    scan_storage_path: str = "/data/scans"
    ai_provider: str = "stub"
    jwt_secret: str = "rousto_dev_jwt_secret_change_me"
    jwt_access_minutes: int = 60
    jwt_refresh_days: int = 7
    otp_dev_mode: bool = True
    otp_dev_code: str = "123456"

    # Security
    allow_legacy_headers: bool = True
    disable_openapi: bool = False
    rate_limit_per_minute: int = 5
    max_upload_bytes: int = 5 * 1024 * 1024

    # Caching (seconds)
    cache_categories_ttl: int = 300
    cache_landing_ttl: int = 120

    # Observability
    sentry_dsn: str = ""
    log_level: str = "INFO"

    # Push notifications (FCM)
    fcm_enabled: bool = False
    fcm_project_id: str = ""
    fcm_credentials_path: str = ""

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    def validate_production(self) -> list[str]:
        warnings: list[str] = []
        if not self.is_production:
            return warnings
        if self.allow_legacy_headers:
            warnings.append("ALLOW_LEGACY_HEADERS must be false in production")
        if self.otp_dev_mode:
            warnings.append("OTP_DEV_MODE must be false in production")
        if self.jwt_secret == "rousto_dev_jwt_secret_change_me":
            warnings.append("JWT_SECRET must be changed in production")
        if self.admin_api_key == "rousto_admin_dev":
            warnings.append("ADMIN_API_KEY must be changed in production")
        if self.cors_origins == "*":
            warnings.append("CORS_ORIGINS should list explicit domains in production")
        return warnings


settings = Settings()
