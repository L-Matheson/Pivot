<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import { Plus, Workflow, MoreHorizontal } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const workspaceId = route.params.workspaceId as string

interface WorkflowStub {
  id: string
  name: string
  updatedAt: string
}

const workflows = ref<WorkflowStub[]>([])

function createNew() {
  const tempId = `new-${Date.now()}`
  router.push({ name: 'workflow-editor', params: { workspaceId, workflowId: tempId } })
}

function openWorkflow(id: string) {
  router.push({ name: 'workflow-editor', params: { workspaceId, workflowId: id } })
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

    <div v-if="workflows.length === 0" class="py-16 text-center">
      <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
        <Workflow class="h-6 w-6 text-muted-foreground" />
      </div>
      <h2 class="font-semibold">No workflows yet</h2>
      <p class="mt-1 mx-auto max-w-xs text-sm text-muted-foreground">
        Create your first workflow to start automating tasks.
      </p>
      <UiButton class="mt-5" @click="createNew" size="sm">
        <Plus class="mr-1 h-4 w-4" />
        Create workflow
      </UiButton>
    </div>

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="wf in workflows"
        :key="wf.id"
        class="text-left"
        @click="openWorkflow(wf.id)"
      >
        <UiCard class="group p-4 transition-colors hover:bg-accent/30">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="rounded-md bg-primary/10 p-2">
                <Workflow class="h-4 w-4 text-primary" />
              </div>
              <div>
                <p class="text-sm font-medium">{{ wf.name }}</p>
                <p class="text-xs text-muted-foreground">Updated {{ wf.updatedAt }}</p>
              </div>
            </div>
            <MoreHorizontal class="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
          </div>
        </UiCard>
      </button>
    </div>
  </div>
</template>
