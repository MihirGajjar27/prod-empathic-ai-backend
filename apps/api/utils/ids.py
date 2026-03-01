import ulid


def _new_id(prefix: str | None = None) -> str:
    """
    Internal helper to generate a ULID-based opaque ID.
    Optionally prepends a prefix for type scoping.
    """
    value = ulid.new().str # 26-char Crockford Base32, sortable
    return f"{prefix}_{value}" if prefix else value


def new_session_id() -> str:
    """
    Generate a unique session identifier for `/v1/sessions` and websocket routing.
    Sortable ULID for chronological debugging.
    """
    return _new_id("sess")


def new_utterance_id() -> str:
    """
    Generate a stable internal utterance identifier independent of provider message IDs.
    """
    return _new_id("utt")


def new_prosody_frame_id() -> str:
    """
    Generate a unique ID for storing `ProsodyFrame` records.
    """
    return _new_id("pf")


def new_receipt_id() -> str:
    """
    Generate a unique receipt identifier for mutation evidence tracking.
    """
    return _new_id("rcpt")


def new_correlation_id() -> str:
    """
    Generate a correlation ID for tracing REST and websocket processing.
    """
    return _new_id("corr")