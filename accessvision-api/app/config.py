from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    cursor_api_key: str = ""
    cursor_model_id: str = "composer-2"
    llm_provider: str = "cursor"
    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:5173,https://access-vision-opal.vercel.app"
    max_upload_mb: int = 50
    llm_timeout_seconds: int = 180

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
