from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    ollama_base_url: str
    echo_llm_model: str
    echo_embed_model: str
    secret_key: str
    echo_dry_run: bool = Field(default=False, description="Skip real LLM calls (tests / CI)")
    codebase_root: str | None = Field(
        default=None,
        description="Optional root for agent read_file tool; defaults to cwd when unset",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore[call-arg]
