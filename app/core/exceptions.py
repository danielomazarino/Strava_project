from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        logger.info(
            "validation_error",
            extra={"action": "validation_error", "outcome": "failure", "path": request.url.path},
        )
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            extra={"action": "unhandled_exception", "outcome": "failure", "path": request.url.path},
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})