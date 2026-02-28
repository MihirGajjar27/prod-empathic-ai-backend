from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from neo4j import GraphDatabase, Driver
from fastapi import Request
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/v1"

    PROJECT_NAME: str = "Empathic-AI"

    SERVICE_NAME: str = "empathic-api"

    VERSION: str = "1.0.0"

    # HUME_API_KEY: str
    # HUME_SECRET_KEY: str
    # HUME_CONFIG_ID: str
    
    # NOTE: We are using VERTEX AI
    # TODO: Add VERTEX AI Keys
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_KG: str = ""

    # TODO: Add Neo4J
    NEO4J_URI: str          = ""
    NEO4J_USERNAME: str     = ""
    NEO4J_PASSWORD: str     = ""
    NEO4J_DATABASE: str     = ""

    CORS_ALLOW_ORIGINS: list[str] = ["*"] # or parsed list

    @field_validator("CORS_ALLOW_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        # supports env like: CORS_ALLOW_ORIGINS="https://a.com,https://b.com"
        if isinstance(v, str):
            items = [x.strip() for x in v.split(",") if x.strip()]
            return items or ["*"]
        return v

    # WS_MAX_SIZE_BYTES: int


# Cached singleton
@lru_cache
def get_settings() -> Settings:
    # NOTE: For now, we won't parse CORS and we will just do a wildcard...
    return Settings()


def create_neo4j_driver() -> Driver:
    """
    This is used for starting/setting up the driver, please do not use this during app usage.
    """
    s = get_settings()
    if not s.NEO4J_URI:
        raise RuntimeError("NEO4J_URI is not set")

    driver = GraphDatabase.driver(
        s.NEO4J_URI,
        auth=(s.NEO4J_USERNAME, s.NEO4J_PASSWORD),
    )

    return driver


def get_neo4j_driver(request: Request) -> Driver:
    """
    This function is used for any Depends(...) usage with getting app state!
    """
    return request.app.state.neo4j_driver


# TODO: Finish this once orchestration
def get_gemini_client() -> any:
    pass


# TODO: Finish this once more dependencies done
def get_hume_http_client():
    pass
