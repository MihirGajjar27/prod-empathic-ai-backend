import logging
import sys
import json
from typing import Any
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Minimal structured JSON log formatter.
    """

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Correlation ID if present
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            base["correlation_id"] = correlation_id

        # Include structured extra fields if provided
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            base.update(extra)

        return json.dumps(base, ensure_ascii=False)


def configure_logging(*, level: str) -> None:
    """
    Configure structured logging globally.
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    # Remove default handlers (important in uvicorn environments)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return project-standard logger instance.
    """
    return logging.getLogger(name)


_ws_logger = get_logger("ws.events")


def log_ws_event(
    *,
    direction: str,
    session_id: str,
    message_type: str,
    correlation_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """
    Emit structured websocket logs.
    """

    if direction not in {"in", "out"}:
        raise ValueError("direction must be 'in' or 'out'")

    safe_extra: dict[str, Any] = {
        "event": "websocket",
        "direction": direction,
        "session_id": session_id,
        "message_type": message_type,
    }

    if extra:
        # Avoid dumping raw payloads
        # Expect already-sanitized metadata only
        safe_extra.update(extra)

    _ws_logger.info(
        "ws_event",
        extra={
            "correlation_id": correlation_id,
            "extra_fields": safe_extra,
        },
    )