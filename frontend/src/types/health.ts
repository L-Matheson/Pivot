// Response from the /api/health endpoint — confirms the API and database are reachable
export interface HealthResponse {
  status: string
  database: string
}
