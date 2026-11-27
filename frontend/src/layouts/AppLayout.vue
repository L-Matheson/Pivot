<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorkspaceStore } from '@/stores/workspace'
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

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const workspaceStore = useWorkspaceStore()
const { applyWorkspaceTheme } = useTheme()

const workspaceId = computed(() => route.params.workspaceId as string)

onMounted(async () => {
  if (workspaceStore.workspaces.length === 0) {
    await workspaceStore.fetchWorkspaces()
  }
  workspaceStore.restoreWorkspace()
  if (!workspaceStore.current || workspaceStore.current.id !== workspaceId.value) {
    const found = workspaceStore.workspaces.find((w) => w.id === workspaceId.value)
    if (found) {
      workspaceStore.selectWorkspace(found)
    } else {
      router.push('/workspaces')
    }
  }
})

watch(
  () => workspaceStore.current?.theme_config,
  (config) => applyWorkspaceTheme(config as Record<string, string> | null),
  { immediate: true },
)

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

function handleLogout() {
  auth.logout()
  workspaceStore.clear()
  router.push('/login')
}
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <aside class="flex w-56 flex-col border-r bg-sidebar">
      <div class="flex items-center gap-3 border-b px-4 py-3">
        <RouterLink
          to="/workspaces"
          class="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
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
              : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground',
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
