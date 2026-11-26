export interface HealthResponse {
  status: string
}

export async function getHealth(fetchFn: typeof fetch = fetch): Promise<HealthResponse> {
  const response = await fetchFn('/api/health')
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`)
  }
  return (await response.json()) as HealthResponse
}
