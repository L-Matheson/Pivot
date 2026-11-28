<script setup lang="ts">
import UiCard from '@/components/ui/card.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-vue-next'
import type { ExecutionStub } from '@/types/execution'

// data

const executions: ExecutionStub[] = []

// constants

const statusConfig = {
  queued: { icon: Clock, label: 'Queued', class: 'text-muted-foreground', bg: 'bg-muted' },
  running: { icon: Loader, label: 'Running', class: 'text-blue-500', bg: 'bg-blue-500/10' },
  succeeded: { icon: CheckCircle, label: 'Succeeded', class: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  failed: { icon: XCircle, label: 'Failed', class: 'text-destructive', bg: 'bg-destructive/10' },
}
</script>

<template>
  <div class="p-8">
    <div class="mb-6">
      <h1 class="text-xl font-semibold tracking-tight">Execution history</h1>
      <p class="mt-1 text-sm text-muted-foreground">Past and active workflow runs</p>
    </div>

    <UiEmptyState
      v-if="executions.length === 0"
      :icon="Clock"
      title="No executions yet"
      description="Execution history will appear here once workflows start running."
    />

    <UiCard v-else class="divide-y">
      <div
        v-for="execution in executions"
        :key="execution.id"
        class="flex items-center justify-between p-4 transition-colors hover:bg-muted"
      >
        <div class="flex items-center gap-3">
          <div :class="['rounded-md p-2', statusConfig[execution.status].bg]">
            <component
              :is="statusConfig[execution.status].icon"
              :class="['h-4 w-4', statusConfig[execution.status].class]"
            />
          </div>
          <div>
            <p class="text-sm font-medium">{{ execution.workflowName }}</p>
            <p class="text-xs text-muted-foreground">{{ execution.startedAt }}</p>
          </div>
        </div>
        <div class="text-right">
          <span
            :class="['inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium', statusConfig[execution.status].class, statusConfig[execution.status].bg]"
          >
            {{ statusConfig[execution.status].label }}
          </span>
          <p class="mt-0.5 text-xs text-muted-foreground">{{ execution.duration }}</p>
        </div>
      </div>
    </UiCard>
  </div>
</template>
