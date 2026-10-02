"""Application settings, read from environment variables (or a local .env file)."""
from decimal import Decimal
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULT_KEY = "change-me-in-development-only"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"  # development | production | test
    app_name: str = "Dragon Wok API"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    # Security
    secret_key: str = INSECURE_DEFAULT_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS: comma separated list of origins
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Database. Either set DATABASE_URL, or the DB_* parts below.
    database_url: str | None = None
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "dragonwok"
    db_password: str = ""
    db_name: str = "dragonwok"
    # TLS (use these for Amazon RDS)
    db_ssl_enabled: bool = False
    db_ssl_ca: str | None = None  # path to the RDS CA bundle (global-bundle.pem)
    db_ssl_verify_identity: bool = True
    db_pool_size: int = 5
    db_pool_recycle: int = 1800

    # Business rules (all money is INR)
    delivery_fee: Decimal = Decimal("40.00")
    tax_rate: Decimal = Decimal("0.05")  # 5%
    free_delivery_above: Decimal = Decimal("0")  # 0 = never free

    # First admin account created by the seed script
    seed_admin_email: str = "admin@example.com"
    seed_admin_password: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{quote_plus(self.db_user)}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    def validate_for_runtime(self) -> None:
        if self.is_production:
            if self.secret_key == INSECURE_DEFAULT_KEY or len(self.secret_key) < 32:
                raise RuntimeError("SECRET_KEY must be set to a random value of 32+ characters in production.")
            if "*" in self.cors_origin_list:
                raise RuntimeError("CORS_ORIGINS must not contain '*' in production.")
            if not self.database_url and not self.db_ssl_enabled:
                raise RuntimeError("DB_SSL_ENABLED must be true in production.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
