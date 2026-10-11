"""RFC-7807 problem responses and application error types."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error rendered as an RFC-7807 problem."""

    status: int = 500
    title: str = "Internal Server Error"
    type_uri: str = "https://nexus.example/errors/internal"

    def __init__(self, detail: str = "", **meta: Any) -> None:
        super().__init__(detail)
        self.detail = detail
        self.meta = meta


class NotFound(AppError):
    status = 404
    title = "Not Found"
    type_uri = "https://nexus.example/errors/not-found"


class Forbidden(AppError):
    status = 403
    title = "Forbidden"
    type_uri = "https://nexus.example/errors/forbidden"


class Unauthorized(AppError):
    status = 401
    title = "Unauthorized"
    type_uri = "https://nexus.example/errors/unauthorized"


class Conflict(AppError):
    status = 409
    title = "Conflict"
    type_uri = "https://nexus.example/errors/conflict"


class Unprocessable(AppError):
    status = 422
    title = "Unprocessable Entity"
    type_uri = "https://nexus.example/errors/unprocessable"


def problem_response(request: Request, exc: AppError) -> JSONResponse:
    body = {
        "type": exc.type_uri,
        "title": exc.title,
        "status": exc.status,
        "detail": exc.detail or exc.title,
        "request_id": str(uuid.uuid4()),
    }
    if exc.meta:
        body["meta"] = exc.meta
    return JSONResponse(status_code=exc.status, content=body)
