import type { RoleRead } from '@/types/role'
import { request } from './client'

export async function listRoles(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<RoleRead[]> {
  return request<RoleRead[]>(
    `/api/workspaces/${workspaceId}/roles`,
    {},
    fetchFn,
  )
}
