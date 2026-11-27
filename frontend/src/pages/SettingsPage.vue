<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkspaceStore } from '@/stores/workspace'
import { useAuthStore } from '@/stores/auth'
import { useUpdateWorkspace, useDeleteWorkspace } from '@/composables/useWorkspaces'
import { useTheme } from '@/composables/useTheme'
import { ApiError } from '@/services/api/client'
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiSpinner from '@/components/ui/spinner.vue'
import { Palette, AlertTriangle, Sun, Moon, Check } from 'lucide-vue-next'

// routing & stores

const router = useRouter()
const workspaceStore = useWorkspaceStore()
const auth = useAuthStore()
const { isDark } = useTheme()

// mutations

const updateMutation = useUpdateWorkspace()
const deleteMutation = useDeleteWorkspace()

// ui state: general

const workspaceName = ref('')
const nameError = ref('')
const nameIsSaved = ref(false)

// ui state: theme

const primaryColor = ref('#4F46E5')
const accentColor = ref('#f0f0f4')
const themeIsSaved = ref(false)
const themeError = ref('')

// ui state: danger zone

const deleteConfirmSlug = ref('')
const deleteError = ref('')

// computed

const isOwner = computed(
  () => workspaceStore.current?.owner_user_id === auth.user?.id,
)

const canDelete = computed(
  () => deleteConfirmSlug.value === workspaceStore.current?.slug,
)

// actions

async function saveName() {
  nameError.value = ''
  nameIsSaved.value = false
  if (!workspaceName.value.trim()) {
    nameError.value = 'Name is required.'
    return
  }
  try {
    await updateMutation.mutateAsync({
      workspaceId: workspaceStore.current!.id,
      body: { name: workspaceName.value.trim() },
    })
    nameIsSaved.value = true
    setTimeout(() => (nameIsSaved.value = false), 2000)
  } catch (e) {
    nameError.value = e instanceof ApiError ? e.detail : 'Failed to save.'
  }
}

async function saveTheme() {
  themeError.value = ''
  themeIsSaved.value = false
  try {
    await updateMutation.mutateAsync({
      workspaceId: workspaceStore.current!.id,
      body: {
        theme_config: {
          primary_color: primaryColor.value,
          accent_color: accentColor.value,
        },
      },
    })
    themeIsSaved.value = true
    setTimeout(() => (themeIsSaved.value = false), 2000)
  } catch (e) {
    themeError.value = e instanceof ApiError ? e.detail : 'Failed to save theme.'
  }
}

async function handleDelete() {
  if (!canDelete.value) return
  deleteError.value = ''
  try {
    await deleteMutation.mutateAsync(workspaceStore.current!.id)
    router.push('/workspaces')
  } catch (e) {
    deleteError.value = e instanceof ApiError ? e.detail : 'Failed to delete workspace.'
  }
}

// constants

const colorModes = [
  { dark: false, label: 'Light', icon: Sun },
  { dark: true, label: 'Dark', icon: Moon },
]

const presetColors = [
  '#4F46E5',
  '#2563EB',
  '#0891B2',
  '#059669',
  '#D97706',
  '#DC2626',
  '#9333EA',
  '#DB2777',
]

// lifecycle

onMounted(() => {
  if (workspaceStore.current) {
    workspaceName.value = workspaceStore.current.name
    const savedTheme = workspaceStore.current.theme_config
    if (savedTheme) {
      if (savedTheme.primary_color) primaryColor.value = savedTheme.primary_color
      if (savedTheme.accent_color) accentColor.value = savedTheme.accent_color
    }
  }
})
</script>

<template>
  <div class="mx-auto max-w-2xl p-8">
    <div class="mb-8">
      <h1 class="text-xl font-semibold tracking-tight">Settings</h1>
      <p class="mt-1 text-sm text-muted-foreground">
        Manage workspace configuration and appearance
      </p>
    </div>

    <!-- General -->
    <UiCard class="p-5">
      <h2 class="mb-4 font-semibold">General</h2>
      <form @submit.prevent="saveName" class="space-y-4">
        <div class="space-y-2">
          <UiLabel for="ws-name">Workspace name</UiLabel>
          <UiInput id="ws-name" v-model="workspaceName" required />
        </div>
        <div class="space-y-2">
          <UiLabel for="ws-slug">URL slug</UiLabel>
          <UiInput id="ws-slug" :model-value="workspaceStore.current?.slug ?? ''" disabled />
          <p class="text-xs text-muted-foreground">The URL slug cannot be changed after creation.</p>
        </div>
        <p v-if="nameError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {{ nameError }}
        </p>
        <UiButton size="sm" :disabled="updateMutation.isPending.value">
          <UiSpinner v-if="updateMutation.isPending.value" class="h-4 w-4" />
          <Check v-else-if="nameIsSaved" class="mr-1 h-4 w-4" />
          <span>{{ nameIsSaved ? 'Saved' : 'Save changes' }}</span>
        </UiButton>
      </form>
    </UiCard>

    <!-- Appearance -->
    <UiCard class="mt-6 p-5">
      <div class="flex items-center gap-2 mb-4">
        <div class="rounded-md bg-primary/10 p-1.5">
          <Palette class="h-4 w-4 text-primary" />
        </div>
        <h2 class="font-semibold">Appearance</h2>
      </div>

      <div class="mb-6">
        <UiLabel class="mb-2 block">Color mode</UiLabel>
        <p class="mb-3 text-xs text-muted-foreground">Defaults to your system preference. Choose below to override.</p>
        <div class="flex gap-2">
          <button
            v-for="mode in colorModes"
            :key="mode.label"
            :class="[
              'flex items-center gap-2 rounded-md border px-3 py-2 text-sm transition-colors',
              isDark === mode.dark
                ? 'border-primary bg-primary/15 text-foreground'
                : 'border-input text-muted-foreground hover:bg-secondary hover:text-foreground',
            ]"
            @click="isDark = mode.dark"
          >
            <component :is="mode.icon" class="h-4 w-4" />
            {{ mode.label }}
          </button>
        </div>
      </div>

      <div>
        <UiLabel class="mb-2 block">Brand colors</UiLabel>
        <p class="mb-3 text-xs text-muted-foreground">
          Applied to all workspace members
        </p>

        <div class="space-y-4">
          <div class="space-y-2">
            <UiLabel>Primary color</UiLabel>
            <div class="flex items-center gap-3">
              <label class="relative cursor-pointer">
                <div
                  class="h-9 w-9 rounded-md border shadow-sm"
                  :style="{ backgroundColor: primaryColor }"
                />
                <input
                  type="color"
                  v-model="primaryColor"
                  class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
                />
              </label>
              <UiInput v-model="primaryColor" class="max-w-28 font-mono text-xs" />
            </div>
            <div class="flex gap-1.5 mt-1">
              <button
                v-for="color in presetColors"
                :key="color"
                class="h-6 w-6 rounded-md border transition-transform hover:scale-110"
                :class="primaryColor === color ? 'ring-2 ring-ring ring-offset-2' : ''"
                :style="{ backgroundColor: color }"
                @click="primaryColor = color"
              />
            </div>
          </div>

          <div class="space-y-2">
            <UiLabel>Accent color</UiLabel>
            <div class="flex items-center gap-3">
              <label class="relative cursor-pointer">
                <div
                  class="h-9 w-9 rounded-md border shadow-sm"
                  :style="{ backgroundColor: accentColor }"
                />
                <input
                  type="color"
                  v-model="accentColor"
                  class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
                />
              </label>
              <UiInput v-model="accentColor" class="max-w-28 font-mono text-xs" />
            </div>
          </div>
        </div>

        <p v-if="themeError" class="mt-3 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {{ themeError }}
        </p>
        <UiButton class="mt-4" size="sm" :disabled="updateMutation.isPending.value" @click="saveTheme">
          <UiSpinner v-if="updateMutation.isPending.value" class="h-4 w-4" />
          <Check v-else-if="themeIsSaved" class="mr-1 h-4 w-4" />
          <span>{{ themeIsSaved ? 'Saved' : 'Save theme' }}</span>
        </UiButton>
      </div>
    </UiCard>

    <!-- Danger zone -->
    <UiCard v-if="isOwner" class="mt-6 border-destructive/30 p-5">
      <div class="flex items-center gap-2 mb-4">
        <div class="rounded-md bg-destructive/10 p-1.5">
          <AlertTriangle class="h-4 w-4 text-destructive" />
        </div>
        <h2 class="font-semibold text-destructive">Danger zone</h2>
      </div>
      <p class="mb-4 text-sm text-muted-foreground">
        Deleting this workspace removes all workflows, connections, and member data permanently.
        This action cannot be undone.
      </p>
      <div class="space-y-3">
        <div class="space-y-2">
          <UiLabel for="delete-confirm">
            Type <span class="font-mono font-semibold text-foreground">{{ workspaceStore.current?.slug }}</span> to confirm
          </UiLabel>
          <UiInput
            id="delete-confirm"
            v-model="deleteConfirmSlug"
            :placeholder="workspaceStore.current?.slug"
          />
        </div>
        <p v-if="deleteError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {{ deleteError }}
        </p>
        <UiButton
          variant="destructive"
          size="sm"
          :disabled="!canDelete || deleteMutation.isPending.value"
          @click="handleDelete"
        >
          <UiSpinner v-if="deleteMutation.isPending.value" class="h-4 w-4" />
          <span v-else>Delete workspace</span>
        </UiButton>
      </div>
    </UiCard>
  </div>
</template>
