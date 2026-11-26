import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { cleanup, render, screen } from '@testing-library/vue'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import App from './App.vue'

const server = setupServer(
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'ok', database: 'ok' })
  }),
)

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(App, {
    global: { plugins: [[VueQueryPlugin, { queryClient }]] },
  })
}

beforeAll(() => server.listen())
afterEach(() => {
  cleanup()
  server.resetHandlers()
})
afterAll(() => server.close())

describe('App', () => {
  it('shows "online" when the backend is healthy', async () => {
    renderApp()
    expect(await screen.findByText('online')).toBeInTheDocument()
  })

  it('shows "unreachable" when the backend returns an error', async () => {
    server.use(
      http.get('/api/health', () => {
        return new HttpResponse(null, { status: 500 })
      }),
    )
    renderApp()
    expect(await screen.findByText('unreachable')).toBeInTheDocument()
  })

  it('shows "unreachable" when the backend is down', async () => {
    server.use(
      http.get('/api/health', () => {
        return HttpResponse.error()
      }),
    )
    renderApp()
    expect(await screen.findByText('unreachable')).toBeInTheDocument()
  })

  it('displays the app heading', () => {
    renderApp()
    expect(screen.getByRole('heading', { name: 'Pivot' })).toBeInTheDocument()
  })
})
