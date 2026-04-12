from __future__ import annotations

from threading import Event

from app.core.config import Settings
from app.workers import background_sync


class FakeThread:
    def __init__(self, *, target, kwargs, name, daemon):
        self.target = target
        self.kwargs = kwargs
        self.name = name
        self.daemon = daemon
        self.started = False

    def start(self):
        self.started = True


def test_start_background_sync_creates_daemon_thread(monkeypatch):
    monkeypatch.setattr(background_sync, "Thread", FakeThread)

    thread, stop_event = background_sync.start_background_sync(settings=Settings(), interval_seconds=123)

    assert thread.started is True
    assert thread.daemon is True
    assert thread.name == "strava-background-sync"
    assert thread.kwargs["interval_seconds"] == 123
    assert isinstance(stop_event, Event)