from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any
from apps.api.core.config import get_neo4j_driver
from apps.api.services.neo4j.repo_sessions import create_session_record, end_session_record, get_top_concepts_for_session
from apps.api.services.summaries import build_session_summary
from neo4j import Driver
import uuid

router = APIRouter(prefix="/sessions", tags=["sessions"])

class CreateSessionRequest(BaseModel):
    client_metadata: Optional[dict[str, Any]] = None
    started_at_ms: Optional[int] = Field(default=None, ge=0)


class SessionResponse(BaseModel):
    session_id: str
    created_at_ms: Optional[int] = Field(default=None, ge=0)
    status: Optional[str]


@router.post("/", response_model=SessionResponse)
async def create_session(
    body: CreateSessionRequest | None = None,
    driver: Driver = Depends(get_neo4j_driver)
) -> SessionResponse:
    body = body or CreateSessionRequest()

    # TODO: Maybe use a session ID() function
    session_id = uuid.uuid4().hex

    # Canonical timestamp
    # Server generated
    import time
    created_at_ms = int(time.time() * 1000)

    await create_session_record(
        driver=driver,
        session_id=session_id,
        created_at_ms=created_at_ms,
        client_metadata=body.client_metadata,
        started_at_ms=body.started_at_ms,
    )

    return SessionResponse(
        session_id=session_id,
    )


class EndSessionResponse(BaseModel):
    summary: str
    top_concepts: list[dict] = []


@router.post("/{session_id}/end", response_model=EndSessionResponse)
async def end_session(
    session_id: str,
    driver: Driver = Depends(get_neo4j_driver),
) -> EndSessionResponse:
    import time
    ended_at_ms = int(time.time() * 1000)

    updated = await end_session_record(driver=driver, session_id=session_id, ended_at_ms=ended_at_ms)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")

    summary = ""
    top_concepts: list[dict] = []

    try:
        top_concepts = await get_top_concepts_for_session(driver=driver, session_id=session_id, limit=10)
    except Exception:
        top_concepts = []

    try:
        summary = await build_session_summary(driver=driver, session_id=session_id)
    except Exception:
        summary = ""

    return EndSessionResponse(
        summary=summary,
        top_concepts=top_concepts
    )
