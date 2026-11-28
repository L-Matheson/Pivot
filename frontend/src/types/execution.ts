export interface NodeResultResponse {
  node_id: string
  status: 'completed' | 'failed' | 'skipped'
  output: Record<string, unknown>
  error: string | null
  duration_ms: number
}

export interface WorkflowRunResponse {
  execution_id: string
  status: 'completed' | 'failed'
  node_results: NodeResultResponse[]
  started_at: string
  finished_at: string
}

export interface ExecutionListItem {
  id: string
  workflow_id: string
  triggered_by: string
  status: 'running' | 'completed' | 'failed'
  error: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string | null
}

export interface NodeExecutionDetail {
  id: string
  node_id: string
  node_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  error: string | null
  duration_ms: number
  started_at: string | null
  finished_at: string | null
}

export interface ExecutionDetail {
  id: string
  workflow_id: string
  triggered_by: string
  status: 'running' | 'completed' | 'failed'
  error: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string | null
  nodes: NodeExecutionDetail[]
}

export type ExecutionStatus = 'queued' | 'running' | 'succeeded' | 'failed'

export interface ExecutionStub {
  id: string
  workflowName: string
  status: ExecutionStatus
  startedAt: string
  duration: string
}
