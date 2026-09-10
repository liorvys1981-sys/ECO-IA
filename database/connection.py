"""Compatibility wrapper around the root database connection module."""

from connection import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
