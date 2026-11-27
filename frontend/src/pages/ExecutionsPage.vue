<script setup lang="ts">
import UiCard from '@/components/ui/card.vue'
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-vue-next'

interface ExecutionStub {
  id: string
  workflowName: string
  status: 'queued' | 'running' | 'succeeded' | 'failed'
  startedAt: string
  duration: string
}

const executions: ExecutionStub[] = []

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

    <div v-if="executions.length === 0" class="py-16 text-center">
      <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
        <Clock class="h-6 w-6 text-muted-foreground" />
      </div>
      <h2 class="font-semibold">No executions yet</h2>
      <p class="mt-1 mx-auto max-w-xs text-sm text-muted-foreground">
        Execution history will appear here once workflows start running.
      </p>
    </div>

    <UiCard v-else class="divide-y">
      <div
        v-for="exec in executions"
        :key="exec.id"
        class="flex items-center justify-between p-4 transition-colors hover:bg-accent/30"
      >
        <div class="flex items-center gap-3">
          <div :class="['rounded-md p-2', statusConfig[exec.status].bg]">
            <component
              :is="statusConfig[exec.status].icon"
              :class="['h-4 w-4', statusConfig[exec.status].class]"
            />
          </div>
          <div>
            <p class="text-sm font-medium">{{ exec.workflowName }}</p>
            <p class="text-xs text-muted-foreground">{{ exec.startedAt }}</p>
          </div>
        </div>
        <div class="text-right">
          <span
            :class="['inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium', statusConfig[exec.status].class, statusConfig[exec.status].bg]"
          >
            {{ statusConfig[exec.status].label }}
          </span>
          <p class="mt-0.5 text-xs text-muted-foreground">{{ exec.duration }}</p>
        </div>
      </div>
    </UiCard>
  </div>
</template>
