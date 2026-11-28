from fastapi import APIRouter

from app.api.connections.oauth import router as oauth_router
from app.api.connections.routes import router as crud_router

router = APIRouter()
router.include_router(crud_router)
router.include_router(oauth_router)
