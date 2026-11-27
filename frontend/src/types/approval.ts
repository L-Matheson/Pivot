export interface ApprovalRequest {
  id: string
  workspace_id: string
  workflow_id: string
  node_id: string
  required_role_id: string
  status: 'pending' | 'approved' | 'denied'
  decided_by: string | null
  decided_at: string | null
  comment: string
  created_at: string
  updated_at: string
}
