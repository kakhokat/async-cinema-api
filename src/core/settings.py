from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "movies"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    ELASTIC_URL: str = "http://127.0.0.1:9200"
    ES_INDEX: str = "movies"

    model_config = SettingsConfigDict(
        env_file=".env,.env.example",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
