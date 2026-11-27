export interface RoleStub {
  name: string
  memberCount: number
  isSystem: boolean
  fullAccess: boolean
}

export interface RoleRead {
  id: string
  workspace_id: string | null
  name: string
  is_system: boolean
  full_access: boolean
  permissions: Record<string, unknown>
}
