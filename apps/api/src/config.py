from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://echo:echo@localhost:5432/echo"
    ollama_base_url: str = "http://localhost:11434"
    echo_llm_model: str = "ollama/gemma4:8b"
    echo_embed_model: str = "nomic-embed-text"
    secret_key: str = "change-me-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
