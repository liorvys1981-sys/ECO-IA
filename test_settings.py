"""Tests for shared ECO-IA settings."""

import importlib
import sys

import pytest


@pytest.fixture(autouse=True)
def reset_settings_module():
    sys.modules.pop("settings", None)
    yield
    sys.modules.pop("settings", None)


def _load_settings():
    import settings

    return importlib.reload(settings)


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("API_PORT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ALERT_EMAILS", raising=False)
    monkeypatch.delenv("COMPOSE_FILE", raising=False)

    settings = _load_settings()

    assert settings.DEBUG is False
    assert settings.API_PORT == 8000
    assert "localhost:5432" in settings.DATABASE_URL
    assert settings.DATABASE_URL.endswith("/eco_ia")
    assert settings.ALERT_EMAILS == []
    assert settings.COMPOSE_FILE.endswith("docker/docker-compose.yml")


def test_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("ALERT_EMAILS", "ops@example.com,admin@example.com")
    monkeypatch.setenv("AUTO_BLOCK_INTRUDERS", "false")

    settings = _load_settings()

    assert settings.DEBUG is True
    assert settings.API_PORT == 9000
    assert settings.ALERT_EMAILS == ["ops@example.com", "admin@example.com"]
    assert settings.AUTO_BLOCK_INTRUDERS is False
