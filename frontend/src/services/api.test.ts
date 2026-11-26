import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { getHealth } from './api'

const server = setupServer(
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'ok', database: 'ok' })
  }),
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('getHealth', () => {
  it('returns the parsed health payload', async () => {
    await expect(getHealth()).resolves.toEqual({ status: 'ok', database: 'ok' })
  })

  it('throws on a non-2xx response', async () => {
    server.use(
      http.get('/api/health', () => {
        return new HttpResponse(null, { status: 503 })
      }),
    )
    await expect(getHealth()).rejects.toThrow('503')
  })
})
