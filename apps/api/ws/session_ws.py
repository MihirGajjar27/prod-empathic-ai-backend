import time
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket

from ws.protocol import (
    EviUserMessagePayload,
    ServerErrorPayload,
    build_ws_envelope,
    parse_client_envelope,
)
from orchestration.kg_updater import process_utterance_event
from services.neo4j import repo_utterances

router = APIRouter(tags=['ws'])


@router.websocket("/ws/session/{session_id}")
async def session_ws_endpoint(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            raw_packet = await websocket.receive_json()
            await process_client_packet(
                session_id=session_id,
                raw_packet=raw_packet,
                websocket=websocket,
            )
    except Exception as e:
        await send_server_error(
            websocket=websocket,
            session_id=session_id,
            code="server_error",
            message="Something went wrong with server",
            retryable=True,
            details={"error": str(e)},
        )
        return


async def receive_client_packet(websocket: WebSocket) -> dict[str, Any]:
    try:
        data = await websocket.receive_json()
        return data
    except Exception as e:
        raise

async def process_client_packet(
    *,
    session_id: str,
    raw_packet: dict[str, Any],
    websocket: WebSocket,
) -> None:
    envelope = parse_client_envelope(raw_packet)

    if envelope.type == "evi.user_message.final":
        await handle_evi_user_message_event(
            session_id=session_id,
            payload=envelope.payload,
            websocket=websocket,
        )
    elif envelope.type == "client.ping":
        pong = build_ws_envelope(
            message_type="server.pong",
            session_id=session_id,
            payload={"server_ts_ms": int(time.time() * 1000)},
            correlation_id=envelope.correlation_id,
        )
        await websocket.send_json(pong)


async def handle_evi_user_message_event(
    *,
    session_id: str,
    payload: dict[str, Any],
    websocket: WebSocket,
) -> None:
    event = EviUserMessagePayload(**payload)

    if event.interim:
        return

    repo_utterances.upsert_utterance(
        utterance_id=str(uuid.uuid4()),
        session_id=session_id,
        role=event.role,
        text=event.content,
        message_id=event.message_id,
        timestamp_ms=event.timestamp_ms,
    )

    if event.prosody_scores:
        repo_utterances.insert_prosody_frame(
            frame_id=str(uuid.uuid4()),
            session_id=session_id,
            message_id=event.message_id,
            top_json=event.prosody_scores,
            created_at_ms=int(time.time() * 1000),
        )

    kg_result = await process_utterance_event(
        session_id=session_id,
        evi_user_message=payload,
    )

    await websocket.send_json(
        build_ws_envelope(
            message_type="kg.diff",
            session_id=session_id,
            payload={
                "nodes_upsert": kg_result.get("nodes_upsert", []),
                "edges_upsert": kg_result.get("edges_upsert", []),
                "receipts": kg_result.get("receipts", []),
            },
        )
    )


async def send_server_error(
    *,
    websocket: WebSocket,
    session_id: str,
    code: str,
    message: str,
    correlation_id: str | None = None,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
) -> None:
    error_payload = ServerErrorPayload(
        code=code,
        message=message,
        correlation_id=correlation_id,
        retryable=retryable,
    ).model_dump()

    if details:
        error_payload["details"] = details

    await websocket.send_json(
        build_ws_envelope(
            message_type="server.error",
            session_id=session_id,
            payload=error_payload,
            correlation_id=correlation_id,
        )
    )
