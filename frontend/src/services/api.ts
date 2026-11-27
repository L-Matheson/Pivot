export interface HealthResponse {
  status: string
  database: string
}

export interface UserRead {
  id: string
  email: string
  display_name: string
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AccessTokenResponse {
  access_token: string
  token_type: string
}

export interface ThemeConfig {
  primary_color?: string
  accent_color?: string
}

export interface WorkspaceRead {
  id: string
  name: string
  slug: string
  owner_user_id: string
  theme_config: ThemeConfig | null
  created_at: string
  updated_at: string
}

export interface WorkspaceUpdateBody {
  name?: string
  theme_config?: ThemeConfig
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  fetchFn: typeof fetch = fetch,
): Promise<T> {
  const token = localStorage.getItem('access_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetchFn(path, { ...options, headers })

  if (response.status === 401 && token) {
    const refreshed = await tryRefresh(fetchFn)
    if (refreshed) {
      headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`
      const retry = await fetchFn(path, { ...options, headers })
      if (!retry.ok) {
        const body = await retry.json().catch(() => ({ detail: retry.statusText }))
        throw new ApiError(retry.status, body.detail ?? retry.statusText)
      }
      return (await retry.json()) as T
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
    throw new ApiError(401, 'Session expired')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new ApiError(response.status, body.detail ?? response.statusText)
  }

  if (response.status === 204) return undefined as T

  return (await response.json()) as T
}

async function tryRefresh(fetchFn: typeof fetch = fetch): Promise<boolean> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return false

  try {
    const response = await fetchFn('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!response.ok) return false
    const data = (await response.json()) as AccessTokenResponse
    localStorage.setItem('access_token', data.access_token)
    return true
  } catch {
    return false
  }
}

export async function getHealth(fetchFn: typeof fetch = fetch): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health', {}, fetchFn)
}

export async function register(
  email: string,
  password: string,
  displayName: string,
  fetchFn: typeof fetch = fetch,
): Promise<UserRead> {
  return request<UserRead>(
    '/api/auth/register',
    {
      method: 'POST',
      body: JSON.stringify({ email, password, display_name: displayName }),
    },
    fetchFn,
  )
}

export async function login(
  email: string,
  password: string,
  fetchFn: typeof fetch = fetch,
): Promise<TokenResponse> {
  return request<TokenResponse>(
    '/api/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    },
    fetchFn,
  )
}

export async function getMe(fetchFn: typeof fetch = fetch): Promise<UserRead> {
  return request<UserRead>('/api/auth/me', {}, fetchFn)
}

export async function listWorkspaces(fetchFn: typeof fetch = fetch): Promise<WorkspaceRead[]> {
  return request<WorkspaceRead[]>('/api/workspaces', {}, fetchFn)
}

export async function createWorkspace(
  name: string,
  slug: string,
  fetchFn: typeof fetch = fetch,
): Promise<WorkspaceRead> {
  return request<WorkspaceRead>(
    '/api/workspaces',
    {
      method: 'POST',
      body: JSON.stringify({ name, slug }),
    },
    fetchFn,
  )
}

export async function getWorkspace(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<WorkspaceRead> {
  return request<WorkspaceRead>(`/api/workspaces/${workspaceId}`, {}, fetchFn)
}

export async function updateWorkspace(
  workspaceId: string,
  body: WorkspaceUpdateBody,
  fetchFn: typeof fetch = fetch,
): Promise<WorkspaceRead> {
  return request<WorkspaceRead>(
    `/api/workspaces/${workspaceId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(body),
    },
    fetchFn,
  )
}

export async function deleteWorkspace(
  workspaceId: string,
  fetchFn: typeof fetch = fetch,
): Promise<void> {
  return request<void>(
    `/api/workspaces/${workspaceId}`,
    { method: 'DELETE' },
    fetchFn,
  )
}
