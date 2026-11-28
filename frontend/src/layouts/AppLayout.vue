<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorkspaceStore } from '@/stores/workspace'
import { useWorkspacesQuery } from '@/composables/useWorkspaces'
import { useTheme } from '@/composables/useTheme'
import UiAvatar from '@/components/ui/avatar.vue'
import UiButton from '@/components/ui/button.vue'
import {
  Workflow,
  Plug,
  Users,
  Shield,
  Clock,
  Settings,
  LogOut,
  ChevronLeft,
} from 'lucide-vue-next'

// routing & stores

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const workspaceStore = useWorkspaceStore()
const { applyWorkspaceTheme } = useTheme()

// data & queries

const workspaceId = computed(() => route.params.workspaceId as string)
const { data: workspaces } = useWorkspacesQuery()

// navigation

const navItems = computed(() => [
  { name: 'workflows', label: 'Workflows', icon: Workflow },
  { name: 'executions', label: 'Executions', icon: Clock },
  { name: 'connections', label: 'Connections', icon: Plug },
  { name: 'members', label: 'Members', icon: Users },
  { name: 'roles', label: 'Roles', icon: Shield },
  { name: 'settings', label: 'Settings', icon: Settings },
])

function isActive(routeName: string) {
  return route.name === routeName || (route.name === 'workflow-editor' && routeName === 'workflows')
}

// actions

async function handleLogout() {
  await auth.logout()
  workspaceStore.clear()
  router.push('/login')
}

// watchers
// Two watches: one syncs the workspace store when the query returns fresh data,
// the other applies the CSS theme variables whenever the selected workspace changes.

watch(workspaces, (workspaceList) => {
  if (!workspaceList) return
  workspaceStore.restoreFromList(workspaceList)
  if (!workspaceStore.current || workspaceStore.current.id !== workspaceId.value) {
    const matchingWorkspace = workspaceList.find((workspace) => workspace.id === workspaceId.value)
    if (matchingWorkspace) {
      workspaceStore.selectWorkspace(matchingWorkspace)
    } else {
      router.push('/workspaces')
    }
  }
}, { immediate: true })

watch(
  () => workspaceStore.current?.theme_config,
  (config) => applyWorkspaceTheme(config as Record<string, string> | null),
  { immediate: true },
)
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <aside class="flex w-56 flex-col border-r bg-sidebar">
      <div class="flex items-center gap-3 border-b px-4 py-3">
        <RouterLink
          to="/workspaces"
          class="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <ChevronLeft class="h-4 w-4" />
        </RouterLink>
        <UiAvatar :name="workspaceStore.current?.name" size="sm" />
        <span class="truncate text-sm font-semibold text-sidebar-foreground">
          {{ workspaceStore.current?.name ?? 'Loading...' }}
        </span>
      </div>

      <nav class="flex-1 px-2 py-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="{ name: item.name, params: { workspaceId } }"
          :class="[
            'group flex items-center gap-3 rounded-md px-3 py-1.5 text-sm transition-colors',
            isActive(item.name)
              ? 'bg-sidebar-accent font-medium text-sidebar-accent-foreground'
              : 'text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
          ]"
        >
          <component
            :is="item.icon"
            :class="[
              'h-4 w-4',
              isActive(item.name) ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground',
            ]"
          />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="border-t px-3 py-3">
        <div class="flex items-center gap-3 px-2">
          <UiAvatar :name="auth.user?.display_name" size="sm" />
          <div class="flex-1 min-w-0">
            <p class="truncate text-sm font-medium text-sidebar-foreground">
              {{ auth.user?.display_name }}
            </p>
            <p class="truncate text-xs text-muted-foreground">
              {{ auth.user?.email }}
            </p>
          </div>
          <UiButton variant="ghost" size="icon" @click="handleLogout" class="h-8 w-8 shrink-0">
            <LogOut class="h-4 w-4" />
          </UiButton>
        </div>
      </div>
    </aside>

    <main class="flex-1 overflow-auto bg-background">
      <RouterView />
    </main>
  </div>
</template>
