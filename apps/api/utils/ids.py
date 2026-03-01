import ulid


def _new_id(prefix: str | None = None) -> str:
    # Support both common ULID package APIs:
    # - `ulid.new().str` from `ulid-py`
    # - `ulid.ulid()` from the lightweight `ulid` module
    if hasattr(ulid, "new"):
        generated = ulid.new()
        value = generated.str if hasattr(generated, "str") else str(generated)
    elif hasattr(ulid, "ulid"):
        value = str(ulid.ulid())
    else:
        raise RuntimeError("Installed ulid module does not expose a supported generator API.")
    return f"{prefix}_{value}" if prefix else value


def new_session_id() -> str:
    return _new_id("sess")


def new_utterance_id() -> str:
    return _new_id("utt")


def new_prosody_frame_id() -> str:
    return _new_id("pf")


def new_receipt_id() -> str:
    return _new_id("rcpt")


def new_correlation_id() -> str:
    return _new_id("corr")
