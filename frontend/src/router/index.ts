import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// route definitions

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/workspaces',
    name: 'workspaces',
    component: () => import('@/pages/WorkspacesPage.vue'),
  },
  {
    path: '/w/:workspaceId',
    component: () => import('@/layouts/AppLayout.vue'),
    children: [
      {
        path: '',
        name: 'workspace-home',
        redirect: (to) => ({ name: 'workflows', params: to.params }),
      },
      {
        path: 'workflows',
        name: 'workflows',
        component: () => import('@/pages/workflows/WorkflowsPage.vue'),
      },
      {
        path: 'workflows/help',
        name: 'workflow-help',
        component: () => import('@/pages/workflows/WorkflowHelpPage.vue'),
      },
      {
        path: 'workflows/:workflowId',
        name: 'workflow-editor',
        component: () => import('@/pages/workflows/WorkflowEditorPage.vue'),
      },
      {
        path: 'connections',
        name: 'connections',
        component: () => import('@/pages/ConnectionsPage.vue'),
      },
      {
        path: 'connections/oauth/:provider/callback',
        name: 'oauth-callback',
        component: () => import('@/pages/OAuthCallbackPage.vue'),
      },
      {
        path: 'members',
        name: 'members',
        component: () => import('@/pages/MembersPage.vue'),
      },
      {
        path: 'roles',
        name: 'roles',
        component: () => import('@/pages/RolesPage.vue'),
      },
      {
        path: 'executions',
        name: 'executions',
        component: () => import('@/pages/ExecutionsPage.vue'),
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/pages/SettingsPage.vue'),
      },
    ],
  },
  {
    path: '/',
    redirect: '/workspaces',
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/workspaces',
  },
]

// router instance

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// navigation guard

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (auth.initializing) {
    await auth.restoreSession()
  }

  if (to.meta.guest) {
    if (auth.user) return { name: 'workspaces' }
    return true
  }

  if (!auth.user) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
