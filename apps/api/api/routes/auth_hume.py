from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import httpx
from apps.api.services.hume.oauth import fetch_access_token
from apps.api.core.config import get_settings
from apps.api.core.main import get_http_client
from typing import Any

router = APIRouter(prefix="/hume", tags=["hume"])


@router.post("/access-token")
async def create_hume_access_token(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> dict[str, Any]:
    settings = get_settings()

    try:
        # Optional: override per-call timeout
        response = await fetch_access_token(
            api_key=settings.HUME_API_KEY,
            secret_key=settings.HUME_SECRET_KEY,
            http_client=http_client,
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=getattr(e, "http_status", 500),
            detail={
                "code": getattr(e, "code", "unknown"),
                "message": getattr(e, "message", str(e)),
                "retryable": getattr(e, "retryable", False),
                "details": getattr(e, "details", None),
            },
        ) from e
