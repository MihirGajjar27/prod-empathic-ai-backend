from typing import Any, Literal
from pydantic import BaseModel
import time

class WsEvenelope(BaseModel):
    type: str
    session_id: str
    payload: dict[str, Any]
    sent_at_ms: int
    correlation_id: str | None = None

class EviUserMessagePayload(BaseModel):
    message_id: str
    role: Literal["user"]
    content: str
    interim: bool = False
    prosody_scores: dict[str, float] | None
    timestamp_ms: int | None

class EviAssistantMessagePayload(BaseModel):
    message_id: str
    role: Literal["assistant"]
    content: str
    timestamp_ms: int | None

class KgDiffPayload(BaseModel):
    nodes_upsert: list[dict]
    edges_upsert: list[dict]
    receipts: list[dict]

class ToolCallsAppliedPayload(BaseModel):
    calls: list[dict]
    dropped_calls: list[dict]

class ServerErrorPayload(BaseModel):
    code: str
    message: str
    correlation_id: str | None
    retryable: bool
    
def parse_client_envelope(raw_packet : dict[str, Any]) -> WsEvenelope:
    return WsEvenelope(**raw_packet)

def build_ws_envelope(
    *,
    message_type: str,
    session_id: str,
    payload: dict[str, Any],
    correlation_id: str | None = None,
) -> dict[str, Any]:
    return {
        "type": message_type,
        "session_id" : session_id,
        "payload" : payload,
        "sent_at_ms" : int(time.time()*1000),
        "correlation_id":correlation_id
    }