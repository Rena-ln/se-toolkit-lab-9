from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_debug: bool = False
    backend_cors_origins: List[str] = ["http://localhost:8080", "http://localhost:5173"]
    backend_api_key: str = "dev-api-key"

    # Database
    database_url: str = "postgresql+asyncpg://deadline_user:deadline_password@postgres:5432/deadlines"

    # OpenTelemetry
    otel_service_name: str = "deadline-optimizer"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


settings = Settings()
