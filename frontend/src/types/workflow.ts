export interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  config: Record<string, unknown>
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  source_handle?: string | null
}

export interface WorkflowDefinition {
  schema_version: number
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface Workflow {
  id: string
  workspace_id: string
  name: string
  description: string
  folder: string | null
  tags: string[]
  definition: WorkflowDefinition
  is_active: boolean
  is_archived: boolean
  created_by: string
  created_at: string
  updated_at: string
}

export interface WorkflowListItem {
  id: string
  name: string
  description: string
  is_active: boolean
  is_archived: boolean
  folder: string | null
  tags: string[]
  created_by: string
  updated_at: string
}
