"""Requested `src` entrypoint for the ECO-IA application."""

from api.main import app, create_app

__all__ = ["app", "create_app"]
