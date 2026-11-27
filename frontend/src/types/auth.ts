export interface UserRead {
  id: string
  email: string
  display_name: string
  is_active: boolean
}

export interface AccessTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}
