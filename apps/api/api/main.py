from fastapi import APIRouter

from .routes import health, sessions, auth, auth_hume, graph

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(sessions.router)
api_router.include_router(auth.router)
api_router.include_router(auth_hume.router)
api_router.include_router(graph.router)
