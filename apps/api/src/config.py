from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    ollama_base_url: str
    echo_llm_model: str
    echo_embed_model: str
    secret_key: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
