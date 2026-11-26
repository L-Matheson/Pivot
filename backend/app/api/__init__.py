from fastapi import APIRouter

from app.api import auth, health, workspaces

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(workspaces.router)
