import type { WorkspaceRead, WorkspaceUpdateBody } from '@/types/workspace'
import { request } from './client'

// Get every workspace the current user belongs to
export async function listWorkspaces(fetchFn: typeof fetch = fetch): Promise<WorkspaceRead[]> {
  return request<WorkspaceRead[]>('/api/workspaces', {}, fetchFn)
}

// Create a new workspace with a display name and a URL-safe slug
export async function createWorkspace(
  name: string,
  slug: string,
  fetchFn: typeof fetch = fetch,
): Promise<WorkspaceRead> {
  return request<WorkspaceRead>(
    '/api/workspaces',
    {
      method: 'POST',
      body: JSON.stringify({ name, slug }),
    },
    fetchFn,
  )
}

// Get a single workspace by its ID
export async function getWorkspace(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<WorkspaceRead> {
  return request<WorkspaceRead>(`/api/workspaces/${workspaceId}`, {}, fetchFn)
}

// Update a workspace's name or theme colors
export async function updateWorkspace(
  workspaceId: string,
  body: WorkspaceUpdateBody,
  fetchFn: typeof fetch = fetch,
): Promise<WorkspaceRead> {
  return request<WorkspaceRead>(
    `/api/workspaces/${workspaceId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(body),
    },
    fetchFn,
  )
}

// Permanently delete a workspace and all its data
export async function deleteWorkspace(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<void> {
  return request<void>(
    `/api/workspaces/${workspaceId}`,
    { method: 'DELETE' },
    fetchFn,
  )
}
