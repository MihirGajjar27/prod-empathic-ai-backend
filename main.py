from fastapi import FastAPI
from apps.api.core.config import settings
from apps.api.api.main import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS, this is important!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)