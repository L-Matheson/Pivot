// Per-workspace brand colors applied to all members via CSS custom properties
export interface ThemeConfig {
  primary_color?: string
  accent_color?: string
}

// A workspace as returned by the backend (list, get, create, update)
export interface WorkspaceRead {
  id: string
  name: string
  slug: string
  owner_user_id: string
  theme_config: ThemeConfig | null
  created_at: string
  updated_at: string
}

// Fields that can be changed on an existing workspace (PATCH /api/workspaces/:id)
export interface WorkspaceUpdateBody {
  name?: string
  theme_config?: ThemeConfig
}
