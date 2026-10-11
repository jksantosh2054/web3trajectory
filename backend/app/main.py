"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.errors import AppError, problem_response


def create_app() -> FastAPI:
    app = FastAPI(
        title="NEXUS API",
        version="1.0.0",
        description="Location-aware Web3 super-app: Date, Market, Navigate, Create, Own-the-insight.",
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return problem_response(request, exc)

    @app.get("/healthz", tags=["ops"])
    async def healthz() -> dict:
        """Liveness probe."""
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"])
    async def readyz() -> dict:
        """Readiness probe (DB/Redis checks land here)."""
        # TODO: ping postgres + redis
        return {"status": "ready"}

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
