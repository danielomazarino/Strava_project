from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import register_exception_handlers


def test_value_error_is_sanitized():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/value-error")
    def value_error_route():
        raise ValueError("bad input")

    client = TestClient(app)

    response = client.get("/value-error")

    assert response.status_code == 400
    assert response.json() == {"detail": "bad input"}


def test_unhandled_exception_is_sanitized():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom_route():
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
