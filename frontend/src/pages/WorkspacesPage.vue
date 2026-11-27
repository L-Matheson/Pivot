<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorkspaceStore } from '@/stores/workspace'
import { useWorkspacesQuery, useCreateWorkspace } from '@/composables/useWorkspaces'
import { ApiError } from '@/services/api/client'
import type { WorkspaceRead } from '@/types/workspace'
import UiButton from '@/components/ui/button.vue'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiCard from '@/components/ui/card.vue'
import UiSpinner from '@/components/ui/spinner.vue'
import UiAvatar from '@/components/ui/avatar.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import { LogOut, Plus, ArrowRight, Workflow, Building2 } from 'lucide-vue-next'

// routing & stores

const router = useRouter()
const auth = useAuthStore()
const workspaceStore = useWorkspaceStore()

// data & queries

const { data: workspaces, isLoading } = useWorkspacesQuery()
const createMutation = useCreateWorkspace()

// ui state

const showCreateForm = ref(false)
const newWorkspaceName = ref('')
const newWorkspaceSlug = ref('')
const createError = ref('')

// actions

function enterWorkspace(workspace: WorkspaceRead) {
  workspaceStore.selectWorkspace(workspace)
  router.push(`/w/${workspace.id}/workflows`)
}

function generateSlug() {
  newWorkspaceSlug.value = newWorkspaceName.value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 80)
}

async function handleCreate() {
  createError.value = ''
  try {
    const created = await createMutation.mutateAsync({ name: newWorkspaceName.value, slug: newWorkspaceSlug.value })
    enterWorkspace(created)
  } catch (e) {
    createError.value = e instanceof ApiError ? e.detail : 'Failed to create workspace.'
  }
}

function handleLogout() {
  auth.logout()
  workspaceStore.clear()
  router.push('/login')
}

// watchers

watch(workspaces, (workspaceList) => {
  if (workspaceList?.length === 1) {
    enterWorkspace(workspaceList[0])
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <header class="flex items-center justify-between border-b px-6 py-3">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Workflow class="h-4 w-4 text-primary-foreground" />
        </div>
        <span class="text-base font-semibold">Pivot</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-muted-foreground">{{ auth.user?.display_name }}</span>
        <UiButton variant="ghost" size="icon" @click="handleLogout">
          <LogOut class="h-4 w-4" />
        </UiButton>
      </div>
    </header>

    <main class="mx-auto w-full max-w-xl flex-1 px-4 py-10">
      <div class="mb-6 flex items-center justify-between">
        <h2 class="text-xl font-semibold tracking-tight">Workspaces</h2>
        <UiButton v-if="!showCreateForm" @click="showCreateForm = true" size="sm">
          <Plus class="mr-1 h-4 w-4" />
          New workspace
        </UiButton>
      </div>

      <UiCard v-if="showCreateForm" class="mb-6 border-primary/20 p-5">
        <h3 class="mb-4 font-semibold">Create workspace</h3>
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div class="space-y-2">
            <UiLabel for="ws-name">Workspace name</UiLabel>
            <UiInput
              id="ws-name"
              v-model="newWorkspaceName"
              placeholder="My Business"
              required
              @input="generateSlug"
            />
          </div>
          <div class="space-y-2">
            <UiLabel for="ws-slug">URL slug</UiLabel>
            <UiInput id="ws-slug" v-model="newWorkspaceSlug" placeholder="my-business" required />
            <p class="text-xs text-muted-foreground">Used in URLs. Letters, numbers, and hyphens only.</p>
          </div>
          <p v-if="createError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {{ createError }}
          </p>
          <div class="flex gap-2">
            <UiButton :disabled="createMutation.isPending.value">
              <UiSpinner v-if="createMutation.isPending.value" class="h-4 w-4" />
              <span v-else>Create</span>
            </UiButton>
            <UiButton variant="ghost" type="button" @click="showCreateForm = false">Cancel</UiButton>
          </div>
        </form>
      </UiCard>

      <div v-if="isLoading" class="flex justify-center py-12">
        <UiSpinner class="h-5 w-5" />
      </div>

      <UiEmptyState
        v-else-if="!workspaces?.length && !showCreateForm"
        :icon="Building2"
        title="No workspaces yet"
        description="Create your first workspace to start building automations."
        action-label="Create workspace"
        :action-icon="Plus"
        @action="showCreateForm = true"
      />

      <div v-else class="space-y-2">
        <button
          v-for="workspace in workspaces"
          :key="workspace.id"
          class="group flex w-full items-center gap-4 rounded-lg border bg-card p-4 text-left transition-colors hover:bg-accent hover:text-accent-foreground"
          @click="enterWorkspace(workspace)"
        >
          <UiAvatar :name="workspace.name" />
          <div class="flex-1 min-w-0">
            <p class="font-medium truncate">{{ workspace.name }}</p>
            <p class="text-sm text-muted-foreground truncate">{{ workspace.slug }}</p>
          </div>
          <ArrowRight class="h-4 w-4 text-muted-foreground transition-colors group-hover:text-foreground" />
        </button>
      </div>
    </main>
  </div>
</template>
