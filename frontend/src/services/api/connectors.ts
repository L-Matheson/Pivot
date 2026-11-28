import type { ConnectorInfo } from '@/types/connection'
import { request } from './client'

export async function listConnectors(
  fetchFn: typeof fetch = fetch,
): Promise<ConnectorInfo[]> {
  return request<ConnectorInfo[]>('/api/connectors', {}, fetchFn)
}
