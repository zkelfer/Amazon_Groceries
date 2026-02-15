from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pantry.db"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    environment: str = "development"
    api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def effective_database_url(self) -> str:
        if self.environment == "production":
            return "sqlite:////home/data/pantry.db"
        return self.database_url

    @property
    def cors_origins(self) -> list[str]:
        origins = [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
        # Never allow wildcard — require explicit origins
        return [o for o in origins if o != "*"]


settings = Settings()
