import type { UserRead, AccessTokenResponse } from '@/types/auth'
import { request } from './client'

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
): Promise<AccessTokenResponse> {
  return request<AccessTokenResponse>(
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

export async function logout(fetchFn: typeof fetch = fetch): Promise<void> {
  return request<void>(
    '/api/auth/logout',
    { method: 'POST' },
    fetchFn,
  )
}
