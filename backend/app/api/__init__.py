from fastapi import APIRouter

from app.api import auth, health, members, roles, workspaces

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(workspaces.router)
router.include_router(members.router)
router.include_router(roles.router)
