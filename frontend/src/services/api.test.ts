import { describe, expect, it, vi } from 'vitest'
import { getHealth } from './api'

describe('getHealth', () => {
  it('returns the parsed health payload', async () => {
    const fetchFn = vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: 'ok' })))
    await expect(getHealth(fetchFn)).resolves.toEqual({ status: 'ok' })
    expect(fetchFn).toHaveBeenCalledWith('/api/health')
  })

  it('throws on a non-2xx response', async () => {
    const fetchFn = vi.fn().mockResolvedValue(new Response('', { status: 503 }))
    await expect(getHealth(fetchFn)).rejects.toThrow('503')
  })
})
