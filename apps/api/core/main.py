from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import config
from contextlib import asynccontextmanager
import httpx


def configure_cors(app: FastAPI) -> None:
    settings = config.get_settings()
    cors_allow_origins = settings.CORS_ALLOW_ORIGINS

    # If not list of strings, put it as a list
    if isinstance(cors_allow_origins, str):
        cors_allow_origins = [cors_allow_origins]
    
    assert isinstance(cors_allow_origins, list)
    assert all(isinstance(x, str) for x in cors_allow_origins)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# NOTE: HTTP Routers is in api/main.py file, and autoamtically included in root main.py file


# TODO: Once WebSockets are done, we can add it here or in the root main.py file or in the ws main.py file
def include_ws_routers(app: FastAPI) -> None:
    pass


def build_lifespan():
    """
    Register startup/shutdown hooks using FastAPI lifespan.

    RETURNS a lifespan async function.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        s = config.get_settings()

        app.state.settings = s
        app.state.neo4j_driver = config.create_neo4j_driver()

        app.state.http_client = httpx.AsyncClient(
            headers={
                "User-Agent": f"{s.SERVICE_NAME}/{s.VERSION}",
                "Accept": "application/json"
            },
        )

        yield

        # Shutdown
        await app.state.http_client.aclose()
        app.state.neo4j_driver.close()

    return lifespan
