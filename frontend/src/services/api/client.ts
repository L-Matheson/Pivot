import type { AccessTokenResponse } from '@/types/auth'

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

// in-memory token state

let accessToken: string | null = null
let refreshTimer: ReturnType<typeof setTimeout> | null = null

export function setAccessToken(token: string, expiresIn: number) {
  accessToken = token
  scheduleRefresh(expiresIn)
}

export function clearAccessToken() {
  accessToken = null
  if (refreshTimer) {
    clearTimeout(refreshTimer)
    refreshTimer = null
  }
}

export function getAccessToken(): string | null {
  return accessToken
}

function scheduleRefresh(expiresIn: number) {
  if (refreshTimer) clearTimeout(refreshTimer)
  const refreshIn = Math.max((expiresIn - 60) * 1000, 0)
  refreshTimer = setTimeout(() => {
    refreshAccessToken()
  }, refreshIn)
}

export async function refreshAccessToken(fetchFn: typeof fetch = fetch): Promise<boolean> {
  try {
    const response = await fetchFn('/api/auth/refresh', {
      method: 'POST',
      credentials: 'include',
    })
    if (!response.ok) return false
    const data = (await response.json()) as AccessTokenResponse
    setAccessToken(data.access_token, data.expires_in)
    return true
  } catch {
    return false
  }
}

// central fetch wrapper

export async function request<T>(
  path: string,
  options: RequestInit = {},
  fetchFn: typeof fetch = fetch,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  const response = await fetchFn(path, { ...options, headers, credentials: 'include' })

  if (response.status === 401 && path !== '/api/auth/refresh') {
    const refreshed = await refreshAccessToken(fetchFn)
    if (refreshed) {
      headers['Authorization'] = `Bearer ${accessToken}`
      const retry = await fetchFn(path, { ...options, headers, credentials: 'include' })
      if (!retry.ok) {
        const body = await retry.json().catch(() => ({ detail: retry.statusText }))
        throw new ApiError(retry.status, body.detail ?? retry.statusText)
      }
      if (retry.status === 204) return undefined as T
      return (await retry.json()) as T
    }
    clearAccessToken()
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
