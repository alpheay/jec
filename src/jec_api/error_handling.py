"""Default error envelope handling for JEC applications."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


SENSITIVE_FIELD_TOKENS = {
    "password",
    "token",
    "authorization",
    "api_key",
    "secret",
}


def utc_timestamp() -> str:
    """Return a UTC ISO 8601 timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def is_sensitive_field(field_name: str) -> bool:
    normalized = field_name.lower()
    return any(token in normalized for token in SENSITIVE_FIELD_TOKENS)


def normalize_request_id(value: str | None) -> str:
    """Normalize request id from header or generate a new one."""
    if value:
        candidate = value.strip()
        if candidate:
            return candidate[:128]
    return f"req_{uuid4().hex}"


def build_error_envelope(
    request_id: str,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a normalized error envelope payload."""
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        },
        "request_id": request_id,
        "timestamp": utc_timestamp(),
    }
    if details:
        payload["error"]["details"] = details
    return payload


def _source_from_validation_location(location: tuple[Any, ...]) -> str:
    if not location:
        return "unknown"
    source = str(location[0])
    return source if source in {"path", "query", "header", "body"} else "unknown"


def _field_from_validation_location(location: tuple[Any, ...]) -> str:
    if not location:
        return "unknown"
    return ".".join(str(part) for part in location[1:]) or "unknown"


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", normalize_request_id(None))


def _http_code_and_message(exc: HTTPException) -> tuple[str, str]:
    status = exc.status_code
    if status == 401:
        return "auth_required", "Authentication is required for this request."
    if status == 403:
        return "forbidden", "You do not have permission to perform this action."
    if status == 404:
        return "not_found", "The requested resource was not found."
    if status == 408:
        return "timeout", "The request timed out."
    if status == 429:
        return "rate_limited", "Too many requests. Please retry later."
    if status >= 500:
        return "internal_error", "An unexpected server error occurred."
    return "validation_error", "One or more request parameters are invalid."


def register_default_error_handlers(app: Any) -> None:
    """Register standardized error envelope handlers for common exceptions."""

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = normalize_request_id(request.headers.get("X-Request-Id"))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        if not getattr(app, "error_envelope", True):
            return JSONResponse(status_code=422, content={"detail": exc.errors()})

        include_details = getattr(app, "error_include_details", True)
        redaction = getattr(app, "error_redaction", True)

        details: list[dict[str, Any]] = []
        if include_details:
            for item in exc.errors():
                location = item.get("loc", ())
                field = _field_from_validation_location(location)
                detail_value: Any = item.get("input")
                if redaction and is_sensitive_field(field):
                    detail_value = "***REDACTED***"

                details.append(
                    {
                        "field": field,
                        "source": _source_from_validation_location(location),
                        "issue": item.get("msg", "Invalid value"),
                        "value": detail_value,
                    }
                )

        payload = build_error_envelope(
            request_id=_get_request_id(request),
            code="validation_error",
            message="One or more request parameters are invalid.",
            details=details or None,
        )
        return JSONResponse(status_code=422, content=payload, headers={"X-Request-Id": _get_request_id(request)})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if not getattr(app, "error_envelope", True):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        code, default_message = _http_code_and_message(exc)
        message = str(exc.detail) if isinstance(exc.detail, str) and exc.detail else default_message
        payload = build_error_envelope(
            request_id=_get_request_id(request),
            code=code,
            message=message,
        )
        return JSONResponse(status_code=exc.status_code, content=payload, headers={"X-Request-Id": _get_request_id(request)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        if not getattr(app, "error_envelope", True):
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        payload = build_error_envelope(
            request_id=_get_request_id(request),
            code="internal_error",
            message="An unexpected server error occurred.",
        )
        return JSONResponse(status_code=500, content=payload, headers={"X-Request-Id": _get_request_id(request)})

