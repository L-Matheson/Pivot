import type { Workflow, WorkflowListItem, WorkflowDefinition } from '@/types/workflow'
import { request } from './client'

export async function listWorkflows(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<WorkflowListItem[]> {
  return request<WorkflowListItem[]>(
    `/api/workspaces/${workspaceId}/workflows`,
    {},
    fetchFn,
  )
}

export async function createWorkflow(
  workspaceId: string,
  body: { name: string; description?: string },
  fetchFn: typeof fetch = fetch,
): Promise<Workflow> {
  return request<Workflow>(
    `/api/workspaces/${workspaceId}/workflows`,
    { method: 'POST', body: JSON.stringify(body) },
    fetchFn,
  )
}

export async function getWorkflow(
  workspaceId: string,
  workflowId: string,
  fetchFn: typeof fetch = fetch,
): Promise<Workflow> {
  return request<Workflow>(
    `/api/workspaces/${workspaceId}/workflows/${workflowId}`,
    {},
    fetchFn,
  )
}

export async function updateWorkflow(
  workspaceId: string,
  workflowId: string,
  body: {
    name?: string
    description?: string
    folder?: string
    tags?: string[]
    definition?: WorkflowDefinition
    is_active?: boolean
  },
  fetchFn: typeof fetch = fetch,
): Promise<Workflow> {
  return request<Workflow>(
    `/api/workspaces/${workspaceId}/workflows/${workflowId}`,
    { method: 'PATCH', body: JSON.stringify(body) },
    fetchFn,
  )
}

export async function duplicateWorkflow(
  workspaceId: string,
  workflowId: string,
  fetchFn: typeof fetch = fetch,
): Promise<Workflow> {
  return request<Workflow>(
    `/api/workspaces/${workspaceId}/workflows/${workflowId}/duplicate`,
    { method: 'POST' },
    fetchFn,
  )
}

export async function archiveWorkflow(
  workspaceId: string,
  workflowId: string,
  fetchFn: typeof fetch = fetch,
): Promise<void> {
  return request<void>(
    `/api/workspaces/${workspaceId}/workflows/${workflowId}/archive`,
    { method: 'POST' },
    fetchFn,
  )
}

export async function deleteWorkflow(
  workspaceId: string,
  workflowId: string,
  fetchFn: typeof fetch = fetch,
): Promise<void> {
  return request<void>(
    `/api/workspaces/${workspaceId}/workflows/${workflowId}`,
    { method: 'DELETE' },
    fetchFn,
  )
}
