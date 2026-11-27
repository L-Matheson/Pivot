export interface ExecutionStub {
  id: string
  workflowName: string
  status: 'queued' | 'running' | 'succeeded' | 'failed'
  startedAt: string
  duration: string
}
