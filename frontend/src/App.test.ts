import { cleanup, render } from '@testing-library/vue'
import { afterEach, describe, expect, it } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'

async function renderApp(path = '/login') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', component: { template: '<div>Login page</div>' } },
      { path: '/workspaces', component: { template: '<div>Workspaces</div>' } },
    ],
  })
  router.push(path)
  await router.isReady()

  const result = render(App, {
    global: { plugins: [router, createPinia()] },
  })
  return result
}

afterEach(() => cleanup())

describe('App', () => {
  it('renders the router view', async () => {
    const { container } = await renderApp('/login')
    expect(container.textContent).toContain('Login page')
  })
})
