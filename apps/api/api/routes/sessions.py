from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any
from apps.api.services.neo4j.repo_sessions import create_session_record, end_session_record, get_top_concepts_for_session, build_session_summary
from fastapi.concurrency import run_in_threadpool
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
) -> SessionResponse:
    body = body or CreateSessionRequest()

    # TODO: Maybe use a session ID() function
    session_id = uuid.uuid4().hex

    # Canonical timestamp
    # Server generated
    import time
    created_at_ms = int(time.time() * 1000)

    # await create_session_record(
    #     session_id=session_id,
    #     created_at_ms=created_at_ms,
    #     # client_metadata=body.client_metadata,
    #     # started_at_ms=body.started_at_ms,
    # )

    await run_in_threadpool(
        create_session_record,
        session_id=session_id,
        created_at_ms=created_at_ms,
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
) -> EndSessionResponse:
    import time
    ended_at_ms = int(time.time() * 1000)

    updated = await run_in_threadpool(
        end_session_record,
        session_id=session_id,
        ended_at_ms=ended_at_ms,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        top_concepts = await run_in_threadpool(
            get_top_concepts_for_session,
            session_id=session_id,
            limit=10,
        )
    except Exception:
        top_concepts = []

    try:
        summary = await run_in_threadpool(build_session_summary, session_id=session_id)
    except Exception:
        summary = ""

    return EndSessionResponse(summary=summary, top_concepts=top_concepts)
