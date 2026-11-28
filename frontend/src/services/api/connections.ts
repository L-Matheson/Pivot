import type {
  ConnectionRead,
  ConnectionListItem,
  OAuthAuthorizeResponse,
  ConnectionTestResult,
} from '@/types/connection'
import { request } from './client'

export async function listConnections(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<ConnectionListItem[]> {
  return request<ConnectionListItem[]>(
    `/api/workspaces/${workspaceId}/connections`,
    {},
    fetchFn,
  )
}

export async function getConnection(
  workspaceId: string,
  connectionId: string,
  fetchFn: typeof fetch = fetch,
): Promise<ConnectionRead> {
  return request<ConnectionRead>(
    `/api/workspaces/${workspaceId}/connections/${connectionId}`,
    {},
    fetchFn,
  )
}

export async function deleteConnection(
  workspaceId: string,
  connectionId: string,
  fetchFn: typeof fetch = fetch,
): Promise<void> {
  return request<void>(
    `/api/workspaces/${workspaceId}/connections/${connectionId}`,
    { method: 'DELETE' },
    fetchFn,
  )
}

export async function testConnection(
  workspaceId: string,
  connectionId: string,
  fetchFn: typeof fetch = fetch,
): Promise<ConnectionTestResult> {
  return request<ConnectionTestResult>(
    `/api/workspaces/${workspaceId}/connections/${connectionId}/test`,
    { method: 'POST' },
    fetchFn,
  )
}

export async function oauthAuthorize(
  workspaceId: string,
  provider: string,
  fetchFn: typeof fetch = fetch,
): Promise<OAuthAuthorizeResponse> {
  return request<OAuthAuthorizeResponse>(
    `/api/workspaces/${workspaceId}/connections/oauth/${provider}/authorize`,
    {},
    fetchFn,
  )
}

export async function oauthCallback(
  workspaceId: string,
  provider: string,
  body: { code: string; state: string },
  fetchFn: typeof fetch = fetch,
): Promise<ConnectionRead> {
  return request<ConnectionRead>(
    `/api/workspaces/${workspaceId}/connections/oauth/${provider}/callback`,
    { method: 'POST', body: JSON.stringify(body) },
    fetchFn,
  )
}
