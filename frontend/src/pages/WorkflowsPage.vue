<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import { Plus, Workflow, MoreHorizontal } from 'lucide-vue-next'
import type { WorkflowStub } from '@/types/workflow'

// routing

const route = useRoute()
const router = useRouter()
const workspaceId = route.params.workspaceId as string

// data

const workflows = ref<WorkflowStub[]>([])

// actions

function createNew() {
  const tempId = `new-${Date.now()}`
  router.push({ name: 'workflow-editor', params: { workspaceId, workflowId: tempId } })
}

function openWorkflow(workflowId: string) {
  router.push({ name: 'workflow-editor', params: { workspaceId, workflowId } })
}
</script>

<template>
  <div class="p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Workflows</h1>
      <UiButton @click="createNew" size="sm">
        <Plus class="mr-1 h-4 w-4" />
        New workflow
      </UiButton>
    </div>

    <UiEmptyState
      v-if="workflows.length === 0"
      :icon="Workflow"
      title="No workflows yet"
      description="Create your first workflow to start automating tasks."
      action-label="Create workflow"
      :action-icon="Plus"
      @action="createNew"
    />

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="workflow in workflows"
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
                <p class="text-xs text-muted-foreground">Updated {{ workflow.updatedAt }}</p>
              </div>
            </div>
            <MoreHorizontal class="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
          </div>
        </UiCard>
      </button>
    </div>
  </div>
</template>
