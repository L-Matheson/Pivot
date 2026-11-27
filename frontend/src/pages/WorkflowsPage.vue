<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import { Plus, Workflow, X } from 'lucide-vue-next'
import { useWorkflowList, useCreateWorkflow } from '@/composables/useWorkflows'

// routing

const route = useRoute()
const router = useRouter()
const workspaceId = computed(() => route.params.workspaceId as string)

// data

const { data: workflows, isLoading } = useWorkflowList(workspaceId)
const createMutation = useCreateWorkflow(workspaceId)

// ui state

const dialogMounted = ref(false)
const dialogVisible = ref(false)
const newName = ref('')
const newDescription = ref('')

// computed

const activeWorkflows = computed(() =>
  (workflows.value ?? []).filter((w) => !w.is_archived),
)

// actions

function openCreateDialog() {
  newName.value = ''
  newDescription.value = ''
  dialogMounted.value = true
  requestAnimationFrame(() => {
    dialogVisible.value = true
  })
  nextTick(() => {
    const el = document.getElementById('workflow-name')
    if (el) el.focus()
  })
}

function closeDialog() {
  dialogVisible.value = false
  setTimeout(() => {
    dialogMounted.value = false
  }, 200)
}

async function submitCreate() {
  if (!newName.value.trim()) return
  const workflow = await createMutation.mutateAsync({
    name: newName.value.trim(),
    description: newDescription.value.trim(),
  })
  closeDialog()
  router.push({
    name: 'workflow-editor',
    params: { workspaceId: workspaceId.value, workflowId: workflow.id },
  })
}

function openWorkflow(workflowId: string) {
  router.push({
    name: 'workflow-editor',
    params: { workspaceId: workspaceId.value, workflowId },
  })
}
</script>

<template>
  <div class="p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Workflows</h1>
      <UiButton @click="openCreateDialog" size="sm">
        <Plus class="mr-1 h-4 w-4" />
        New workflow
      </UiButton>
    </div>

    <div v-if="isLoading" class="flex justify-center py-16">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>

    <UiEmptyState
      v-else-if="activeWorkflows.length === 0"
      :icon="Workflow"
      title="No workflows yet"
      description="Create your first workflow to start automating tasks."
      action-label="Create workflow"
      :action-icon="Plus"
      @action="openCreateDialog"
    />

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="workflow in activeWorkflows"
        :key="workflow.id"
        class="text-left"
        @click="openWorkflow(workflow.id)"
      >
        <UiCard class="group p-4 transition-colors hover:bg-accent hover:text-accent-foreground">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="rounded-md bg-primary/10 p-2">
                <Workflow class="h-4 w-4 text-primary" />
              </div>
              <div>
                <p class="text-sm font-medium">{{ workflow.name }}</p>
                <p v-if="workflow.description" class="text-xs text-muted-foreground line-clamp-1">
                  {{ workflow.description }}
                </p>
              </div>
            </div>
            <span
              class="mt-0.5 inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium"
              :class="workflow.is_active
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                : 'bg-muted text-muted-foreground'"
            >
              {{ workflow.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </UiCard>
      </button>
    </div>

    <!-- create dialog -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="dialogMounted"
          class="fixed inset-0 z-50 flex items-center justify-center"
          :class="dialogVisible ? 'pointer-events-auto' : 'pointer-events-none'"
        >
          <!-- backdrop -->
          <div
            class="absolute inset-0 bg-black/50 transition-opacity duration-200"
            :class="dialogVisible ? 'opacity-100' : 'opacity-0'"
            @click="closeDialog"
          />

          <!-- card -->
          <div
            class="relative z-10 w-full max-w-md rounded-lg border bg-background p-6 shadow-lg transition-all duration-200"
            :class="dialogVisible
              ? 'opacity-100 scale-100 translate-y-0'
              : 'opacity-0 scale-95 translate-y-2'"
          >
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-semibold">New Workflow</h2>
                <p class="text-sm text-muted-foreground">Give it a name so you can find it later.</p>
              </div>
              <button
                class="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                @click="closeDialog"
              >
                <X class="h-4 w-4" />
              </button>
            </div>

            <form @submit.prevent="submitCreate" class="space-y-4">
              <div>
                <UiLabel for="workflow-name">Name</UiLabel>
                <UiInput
                  id="workflow-name"
                  ref="nameInputRef"
                  v-model="newName"
                  placeholder="e.g. Invoice Processor"
                  class="mt-1"
                />
              </div>
              <div>
                <UiLabel for="workflow-desc">Description <span class="text-muted-foreground font-normal">(optional)</span></UiLabel>
                <UiInput
                  id="workflow-desc"
                  v-model="newDescription"
                  placeholder="What does this workflow do?"
                  class="mt-1"
                />
              </div>
              <div class="flex justify-end gap-2 pt-2">
                <UiButton variant="ghost" type="button" @click="closeDialog">
                  Cancel
                </UiButton>
                <UiButton type="submit" :disabled="!newName.trim() || createMutation.isPending.value">
                  {{ createMutation.isPending.value ? 'Creating...' : 'Create & open editor' }}
                </UiButton>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
