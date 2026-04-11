from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    openrouter_api_key: SecretStr
    echo_llm_model: str = "openrouter/free"
    echo_llm_app_name: str = "echo"
    ollama_base_url: str = "http://localhost:11434"
    echo_embed_model: str = "nomic-embed-text:latest"
    echo_dry_run: bool = Field(default=False, description="Skip real LLM calls (tests / CI)")
    codebase_root: str | None = Field(
        default=None,
        description="Optional root for agent read_file tool; defaults to cwd when unset",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore[call-arg]
