// Barrel file — import from '@/services/api' to get everything in one place.
// Each domain's routes and types live in their own file so changes stay isolated.

export { ApiError, request } from './client'
export { setAccessToken, clearAccessToken, getAccessToken, refreshAccessToken } from './client'
export { register, login, getMe, logout } from './auth'
export { listWorkspaces, createWorkspace, getWorkspace, updateWorkspace, deleteWorkspace } from './workspaces'
export { getHealth } from './health'

export type { HealthResponse } from '@/types/health'
export type { UserRead, AccessTokenResponse } from '@/types/auth'
export type { ThemeConfig, WorkspaceRead, WorkspaceUpdateBody } from '@/types/workspace'
