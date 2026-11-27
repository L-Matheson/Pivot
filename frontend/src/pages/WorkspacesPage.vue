<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorkspaceStore } from '@/stores/workspace'
import { ApiError } from '@/services/api'
import UiButton from '@/components/ui/button.vue'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiCard from '@/components/ui/card.vue'
import UiSpinner from '@/components/ui/spinner.vue'
import UiAvatar from '@/components/ui/avatar.vue'
import { LogOut, Plus, ArrowRight, Workflow, Building2 } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const workspaceStore = useWorkspaceStore()

const showCreate = ref(false)
const newName = ref('')
const newSlug = ref('')
const createError = ref('')
const creating = ref(false)

onMounted(async () => {
  await workspaceStore.fetchWorkspaces()
  if (workspaceStore.workspaces.length === 1) {
    enterWorkspace(workspaceStore.workspaces[0].id)
  }
})

function enterWorkspace(id: string) {
  const ws = workspaceStore.workspaces.find((w) => w.id === id)
  if (ws) workspaceStore.selectWorkspace(ws)
  router.push(`/w/${id}/workflows`)
}

function generateSlug() {
  newSlug.value = newName.value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 80)
}

async function handleCreate() {
  createError.value = ''
  creating.value = true
  try {
    const ws = await workspaceStore.createWorkspace(newName.value, newSlug.value)
    enterWorkspace(ws.id)
  } catch (e) {
    createError.value = e instanceof ApiError ? e.detail : 'Failed to create workspace.'
  } finally {
    creating.value = false
  }
}

function handleLogout() {
  auth.logout()
  workspaceStore.clear()
  router.push('/login')
}
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
        <UiButton v-if="!showCreate" @click="showCreate = true" size="sm">
          <Plus class="mr-1 h-4 w-4" />
          New workspace
        </UiButton>
      </div>

      <UiCard v-if="showCreate" class="mb-6 border-primary/20 p-5">
        <h3 class="mb-4 font-semibold">Create workspace</h3>
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div class="space-y-2">
            <UiLabel for="ws-name">Workspace name</UiLabel>
            <UiInput
              id="ws-name"
              v-model="newName"
              placeholder="My Business"
              required
              @input="generateSlug"
            />
          </div>
          <div class="space-y-2">
            <UiLabel for="ws-slug">URL slug</UiLabel>
            <UiInput id="ws-slug" v-model="newSlug" placeholder="my-business" required />
            <p class="text-xs text-muted-foreground">Used in URLs. Letters, numbers, and hyphens only.</p>
          </div>
          <p v-if="createError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {{ createError }}
          </p>
          <div class="flex gap-2">
            <UiButton :disabled="creating">
              <UiSpinner v-if="creating" class="h-4 w-4" />
              <span v-else>Create</span>
            </UiButton>
            <UiButton variant="ghost" type="button" @click="showCreate = false">Cancel</UiButton>
          </div>
        </form>
      </UiCard>

      <div v-if="workspaceStore.loading" class="flex justify-center py-12">
        <UiSpinner class="h-5 w-5" />
      </div>

      <div v-else-if="workspaceStore.workspaces.length === 0 && !showCreate" class="py-16 text-center">
        <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
          <Building2 class="h-6 w-6 text-muted-foreground" />
        </div>
        <h3 class="font-semibold">No workspaces yet</h3>
        <p class="mt-1 mx-auto max-w-xs text-sm text-muted-foreground">
          Create your first workspace to start building automations.
        </p>
        <UiButton class="mt-5" @click="showCreate = true">
          <Plus class="mr-1 h-4 w-4" />
          Create workspace
        </UiButton>
      </div>

      <div v-else class="space-y-2">
        <button
          v-for="ws in workspaceStore.workspaces"
          :key="ws.id"
          class="group flex w-full items-center gap-4 rounded-lg border bg-card p-4 text-left transition-colors hover:bg-accent/50"
          @click="enterWorkspace(ws.id)"
        >
          <UiAvatar :name="ws.name" />
          <div class="flex-1 min-w-0">
            <p class="font-medium truncate">{{ ws.name }}</p>
            <p class="text-sm text-muted-foreground truncate">{{ ws.slug }}</p>
          </div>
          <ArrowRight class="h-4 w-4 text-muted-foreground transition-colors group-hover:text-foreground" />
        </button>
      </div>
    </main>
  </div>
</template>
