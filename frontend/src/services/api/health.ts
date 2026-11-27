import type { HealthResponse } from '@/types/health'
import { request } from './client'

// Quick check that the API and database are both reachable
export async function getHealth(fetchFn: typeof fetch = fetch): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health', {}, fetchFn)
}
