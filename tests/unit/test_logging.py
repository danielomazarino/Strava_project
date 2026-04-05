from __future__ import annotations

import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_emits_structured_payload():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="strava",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="startup complete",
        args=(),
        exc_info=None,
    )
    record.action = "startup"
    record.outcome = "success"
    record.user_id = 123
    record.path = "/health"

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "strava"
    assert payload["message"] == "startup complete"
    assert payload["action"] == "startup"
    assert payload["outcome"] == "success"
    assert payload["user_id"] == "123"
    assert payload["path"] == "/health"
    assert "timestamp" in payload
