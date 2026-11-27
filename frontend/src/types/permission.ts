export interface PermissionAction {
  slug: string
  label: string
}

export interface PermissionResource {
  slug: string
  label: string
  actions: PermissionAction[]
}
