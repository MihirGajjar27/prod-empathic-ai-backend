from fastapi import FastAPI
from apps.api.core.config import get_settings
from apps.api.api.main import api_router
from apps.api.core.main import configure_cors, build_lifespan

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=build_lifespan()
)

# CORS, this is important!
configure_cors(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
