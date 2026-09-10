"""Combined API router for the requested `src/services/api` layout."""

from fastapi import APIRouter

from api.routes import admin, services, webhooks

router = APIRouter()
router.include_router(services.router)
router.include_router(admin.router)
router.include_router(webhooks.router)

__all__ = ["router"]
