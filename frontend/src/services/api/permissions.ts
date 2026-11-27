import type { PermissionResource } from '@/types/permission'
import { request } from './client'

export async function listPermissions(
  fetchFn: typeof fetch = fetch,
): Promise<PermissionResource[]> {
  return request<PermissionResource[]>('/api/permissions', {}, fetchFn)
}
