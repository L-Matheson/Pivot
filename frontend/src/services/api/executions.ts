import type { WorkflowRunResponse, ExecutionListItem, ExecutionDetail } from '@/types/execution'
import { request } from './client'

export async function runWorkflow(
  workspaceId: string,
  workflowId: string,
  fetchFn: typeof fetch = fetch,
): Promise<WorkflowRunResponse> {
  return request<WorkflowRunResponse>(
    `/api/workspaces/${workspaceId}/workflows/${workflowId}/run`,
    { method: 'POST' },
    fetchFn,
  )
}

export async function listExecutions(
  workspaceId: string,
  workflowId?: string,
  fetchFn: typeof fetch = fetch,
): Promise<ExecutionListItem[]> {
  const params = workflowId ? `?workflow_id=${workflowId}` : ''
  return request<ExecutionListItem[]>(
    `/api/workspaces/${workspaceId}/executions${params}`,
    {},
    fetchFn,
  )
}

export async function getExecution(
  workspaceId: string,
  executionId: string,
  fetchFn: typeof fetch = fetch,
): Promise<ExecutionDetail> {
  return request<ExecutionDetail>(
    `/api/workspaces/${workspaceId}/executions/${executionId}`,
    {},
    fetchFn,
  )
}
