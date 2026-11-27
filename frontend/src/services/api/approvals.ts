import type { ApprovalRequest } from '@/types/approval'
import { request } from './client'

export async function listApprovals(
  workspaceId: string,
  status?: string,
  fetchFn: typeof fetch = fetch,
): Promise<ApprovalRequest[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return request<ApprovalRequest[]>(
    `/api/workspaces/${workspaceId}/approvals${query}`,
    {},
    fetchFn,
  )
}

export async function createApproval(
  workspaceId: string,
  body: { workflow_id: string; node_id: string; required_role_id: string },
  fetchFn: typeof fetch = fetch,
): Promise<ApprovalRequest> {
  return request<ApprovalRequest>(
    `/api/workspaces/${workspaceId}/approvals`,
    { method: 'POST', body: JSON.stringify(body) },
    fetchFn,
  )
}

export async function getApproval(
  workspaceId: string,
  approvalId: string,
  fetchFn: typeof fetch = fetch,
): Promise<ApprovalRequest> {
  return request<ApprovalRequest>(
    `/api/workspaces/${workspaceId}/approvals/${approvalId}`,
    {},
    fetchFn,
  )
}

export async function decideApproval(
  workspaceId: string,
  approvalId: string,
  body: { decision: 'approved' | 'denied'; comment?: string },
  fetchFn: typeof fetch = fetch,
): Promise<ApprovalRequest> {
  return request<ApprovalRequest>(
    `/api/workspaces/${workspaceId}/approvals/${approvalId}/decide`,
    { method: 'POST', body: JSON.stringify(body) },
    fetchFn,
  )
}
