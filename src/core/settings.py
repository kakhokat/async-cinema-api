from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "movies"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    ELASTIC_URL: str = "http://127.0.0.1:9200"
    ES_INDEX: str = "movies"

    # Docs / OpenAPI
    DOCS_URL: str = "/api/openapi"
    OPENAPI_URL: str = "/api/openapi.json"

    # CORS / Proxy
    CORS_ALLOW_ORIGINS: str = "*"
    PROXY_TRUSTED_HOSTS: str = "*"

    # Pagination
    PAGE_SIZE_DEFAULT: int = 50
    PAGE_SIZE_MAX: int = 1000

    # Cache
    FILM_CACHE_TTL: int = 300

    # ES loader
    ES_WAIT_TIMEOUT: int = 60
    ES_MAPPING_PATH: str = "data/movies.mapping.json"
    ES_BULK_PATH: str = "data/movies.bulk.ndjson"

    model_config = SettingsConfigDict(
        env_file=".env,.env.example",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
