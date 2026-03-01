from typing import Any

from fastapi import APIRouter, WebSocket

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
            code = "server error",
            message = "Something went wrong with server",
            retryable=True
            details={"error" : str(e)},
        )
        return


async def receive_client_packet(websocket: WebSocket) -> dict[str,Any]:

    pass

async def process_client_packet(
        *,
        session_id: str,
        raw_packet: dict[str,Any],
        websocket: WebSocket,
) -> None:
    
    pass

async def handle_evi_user_message_event(
        *,
        session_id: str,
        payload: dict[str, Any],
        websocket: WebSocket,
) -> None:
    pass


async def send_server_error(
        *,
        websocket: WebSocket,
        session_id: str,
        code: str,
        correaltion_id: str | None = None,
        retryable: bool = False,
        details: dict[str,Any] | None = None,
) -> None: 
    pass

