from typing import Any
from fastapi import HTTPException

class AppError(Exception):
    def __init__(
            self, 
            *,
            code: str,
            message: str,
            http_status: int = 400,
            retryable: bool = False,
            correlation_id: str | None = None,
            details: dict[str, Any] | None = None
    ):
        self.code = code
        self.http_status = http_status
        self.retryable = retryable
        self.correlation_id = correlation_id
        self.details = details
        super().__init__(message)

def to_http_exception(error: AppError) -> Any:
    return HTTPException(
        status_code=error.http_status,
        detail={
            "code": error.code,
            "message": error.message,
            "correlation_id": error.correlation_id,
            },
        )
def to_server_error_payload(error: Exception, *, correlation_id: str | None = None) -> dict[str, Any]:
    pass
