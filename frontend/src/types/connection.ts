export interface ConnectionRead {
  id: string
  workspace_id: string
  provider: string
  name: string
  auth_type: string
  scopes: string
  status: 'connected' | 'expired' | 'error'
  connected_by_user_id: string
  created_at: string
  updated_at: string
}

export interface ConnectionListItem {
  id: string
  provider: string
  name: string
  auth_type: string
  scopes: string
  status: 'connected' | 'expired' | 'error'
  connected_by_user_id: string
  updated_at: string
}

export interface OAuthAuthorizeResponse {
  authorize_url: string
  state: string
}

export interface ConnectionTestResult {
  connection_id: string
  ok: boolean
  message: string
}

export interface ConnectorInfo {
  slug: string
  display_name: string
  icon: string
  auth_type: string
  description: string
  triggers: string[]
  actions: string[]
  scopes?: string[]
}
