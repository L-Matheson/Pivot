from fastapi import APIRouter

from app.api import (
    approvals,
    auth,
    connections,
    connectors,
    executions,
    health,
    members,
    permissions,
    roles,
    workflows,
    workspaces,
)

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(workspaces.router)
router.include_router(members.router)
router.include_router(roles.router)
router.include_router(workflows.router)
router.include_router(executions.router)
router.include_router(approvals.router)
router.include_router(permissions.router)
router.include_router(connections.router)
router.include_router(connectors.router)
