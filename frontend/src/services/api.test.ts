import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth } from './api'

afterEach(() => {
  localStorage.clear()
})

describe('getHealth', () => {
  it('returns the parsed health payload', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ status: 'ok', database: 'ok' }),
    })
    await expect(getHealth(mockFetch)).resolves.toEqual({ status: 'ok', database: 'ok' })
  })

  it('throws on a non-2xx response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable',
      json: () => Promise.resolve({ detail: 'Service Unavailable' }),
    })
    await expect(getHealth(mockFetch)).rejects.toThrow('Service Unavailable')
  })
})
