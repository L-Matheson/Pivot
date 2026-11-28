// Barrel file — import from '@/services/api' to get everything in one place.
// Each domain's routes and types live in their own file so changes stay isolated.

export { ApiError, request } from './client'
export { setAccessToken, clearAccessToken, getAccessToken, refreshAccessToken } from './client'
export { register, login, getMe, logout } from './auth'
export { listWorkspaces, createWorkspace, getWorkspace, updateWorkspace, deleteWorkspace } from './workspaces'
export { getHealth } from './health'
export {
  listWorkflows,
  createWorkflow,
  getWorkflow,
  updateWorkflow,
  duplicateWorkflow,
  archiveWorkflow,
  deleteWorkflow,
} from './workflows'
export { listRoles } from './roles'
export { listPermissions } from './permissions'
export {
  listApprovals,
  createApproval,
  getApproval,
  decideApproval,
} from './approvals'
export {
  listConnections,
  getConnection,
  deleteConnection,
  testConnection,
  oauthAuthorize,
  oauthCallback,
} from './connections'
export { listConnectors } from './connectors'

export type { HealthResponse } from '@/types/health'
export type { UserRead, AccessTokenResponse } from '@/types/auth'
export type { ThemeConfig, WorkspaceRead, WorkspaceUpdateBody } from '@/types/workspace'
export type {
  Workflow,
  WorkflowListItem,
  WorkflowDefinition,
  WorkflowNode,
  WorkflowEdge,
} from '@/types/workflow'
export type { RoleRead } from '@/types/role'
export type { PermissionResource, PermissionAction } from '@/types/permission'
export { runWorkflow, listExecutions, getExecution } from './executions'
export type { ApprovalRequest } from '@/types/approval'
export type {
  ConnectionRead,
  ConnectionListItem,
  OAuthAuthorizeResponse,
  ConnectionTestResult,
  ConnectorInfo,
} from '@/types/connection'
export type {
  WorkflowRunResponse,
  NodeResultResponse,
  ExecutionListItem,
  ExecutionDetail,
  NodeExecutionDetail,
} from '@/types/execution'
