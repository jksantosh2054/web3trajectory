"""Application configuration via environment (pydantic-settings)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database / broker
    database_url: str = "postgresql+psycopg://nexus:nexus@postgres:5432/nexus"
    redis_url: str = "redis://redis:6379/0"

    # Auth
    secret_key: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # App
    api_base_url: str = "http://localhost:8000"
    web_base_url: str = "http://localhost:3000"
    environment: str = "local"  # local | ci | staging | production

    # Settlement: fiat | simulated | onchain.
    # Nepal production MUST be "fiat" (crypto settlement disabled pending legal clearance).
    settlement_mode: str = "simulated"
    platform_fee_pct: float = 5.0

    # Payments (fiat rail)
    esewa_merchant_id: str = ""
    esewa_secret_key: str = ""
    esewa_base_url: str = "https://rc-epay.esewa.com.np"
    khalti_public_key: str = ""
    khalti_secret_key: str = ""
    khalti_base_url: str = "https://dev.khalti.com/api/v2"

    # KMS
    kms_provider: str = "local_dev"
    kms_url: str = ""
    kms_token: str = ""

    # Object storage
    s3_endpoint: str = "http://storage:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "nexus"

    # Chain
    chain_rpc_url: str = "http://chain:8545"
    chain_id: int = 31337
    insight_token_address: str = ""
    auction_house_address: str = ""

    def is_nepal_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
