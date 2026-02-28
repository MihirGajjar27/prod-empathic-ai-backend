from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any
from apps.api.core.config import get_neo4j_driver
from apps.api.services.neo4j.repo_graph import get_graph_snapshot
from neo4j import Driver

router = APIRouter(prefix="/sessions", tags=["graph"])


@router.get("/{session_id}/graph")
async def get_session_graph(
    session_id: str,
    driver: Driver = Depends(get_neo4j_driver),
) -> dict[str, list[dict]]:
    snapshot = await get_graph_snapshot(driver=driver, session_id=session_id)

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return snapshot
