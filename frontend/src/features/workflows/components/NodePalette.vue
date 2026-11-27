<script setup lang="ts">
import {
  Mail,
  Send,
  FileSpreadsheet,
  Bell,
  Globe,
  Webhook,
  Clock,
  Database,
  Search,
  Play,
  Shuffle,
  Timer,
  GitBranch,
  Repeat,
  GitFork,
  HelpCircle,
} from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()
const workspaceId = route.params.workspaceId as string

const triggers = [
  { type: 'trigger', label: 'Manual Run', icon: Play, desc: 'Start by clicking Run' },
  { type: 'trigger', label: 'Email Received', icon: Mail, desc: 'Fires on matching email' },
  { type: 'trigger', label: 'Webhook', icon: Webhook, desc: 'Fires on incoming POST' },
  { type: 'trigger', label: 'Schedule', icon: Clock, desc: 'Fires on a cron schedule' },
  { type: 'trigger', label: 'Database Change', icon: Database, desc: 'Polls for new rows' },
  { type: 'trigger', label: 'API Poll', icon: Search, desc: 'Polls an API endpoint' },
]

const actions = [
  { type: 'action', label: 'Send Email', icon: Send, desc: 'Send via connected account' },
  { type: 'action', label: 'Send Notification', icon: Bell, desc: 'Notify user or channel' },
  { type: 'action', label: 'Write to Sheet', icon: FileSpreadsheet, desc: 'Append row to spreadsheet' },
  { type: 'action', label: 'HTTP Request', icon: Globe, desc: 'Call any REST endpoint' },
  { type: 'action', label: 'Transform Data', icon: Shuffle, desc: 'Map, filter, or format' },
  { type: 'action', label: 'Delay', icon: Timer, desc: 'Wait before continuing' },
]

const logic = [
  { type: 'condition', label: 'If / Else', icon: GitBranch, desc: 'Branch on a condition' },
  { type: 'loop', label: 'Loop', icon: Repeat, desc: 'Iterate over a list' },
  { type: 'parallel', label: 'Parallel', icon: GitFork, desc: 'Fan-out to branches' },
]

function onDragStart(event: DragEvent, type: string, label: string) {
  if (!event.dataTransfer) return
  event.dataTransfer.setData('application/pivot-node-type', type)
  event.dataTransfer.setData('application/pivot-node-label', label)
  event.dataTransfer.effectAllowed = 'move'
}
</script>

<template>
  <aside class="w-64 overflow-y-auto border-r bg-sidebar p-4">
    <div class="mb-3 flex items-center justify-between">
      <p class="text-xs font-medium text-muted-foreground">Nodes</p>
      <RouterLink
        :to="{ name: 'workflow-help', params: { workspaceId } }"
        class="flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
      >
        <HelpCircle class="h-3 w-3" />
        Help
      </RouterLink>
    </div>

    <p class="mb-2 text-xs font-medium text-emerald-600 dark:text-emerald-400">Triggers</p>
    <div class="space-y-1">
      <div
        v-for="node in triggers"
        :key="node.label"
        class="flex cursor-grab items-center gap-2.5 rounded-md border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 transition-colors hover:border-emerald-500/40 active:cursor-grabbing"
        draggable="true"
        @dragstart="onDragStart($event, node.type, node.label)"
      >
        <component :is="node.icon" class="h-4 w-4 shrink-0 text-emerald-500" />
        <div class="min-w-0">
          <span class="block text-sm font-medium leading-tight">{{ node.label }}</span>
          <span class="block text-[10px] leading-tight text-muted-foreground">{{ node.desc }}</span>
        </div>
      </div>
    </div>

    <div class="my-3 h-px bg-border" />

    <p class="mb-2 text-xs font-medium text-blue-600 dark:text-blue-400">Actions</p>
    <div class="space-y-1">
      <div
        v-for="node in actions"
        :key="node.label"
        class="flex cursor-grab items-center gap-2.5 rounded-md border border-blue-500/20 bg-blue-500/5 px-3 py-2 transition-colors hover:border-blue-500/40 active:cursor-grabbing"
        draggable="true"
        @dragstart="onDragStart($event, node.type, node.label)"
      >
        <component :is="node.icon" class="h-4 w-4 shrink-0 text-blue-500" />
        <div class="min-w-0">
          <span class="block text-sm font-medium leading-tight">{{ node.label }}</span>
          <span class="block text-[10px] leading-tight text-muted-foreground">{{ node.desc }}</span>
        </div>
      </div>
    </div>

    <div class="my-3 h-px bg-border" />

    <p class="mb-2 text-xs font-medium text-amber-600 dark:text-amber-400">Logic</p>
    <div class="space-y-1">
      <div
        v-for="node in logic"
        :key="node.label"
        class="flex cursor-grab items-center gap-2.5 rounded-md border border-amber-500/20 bg-amber-500/5 px-3 py-2 transition-colors hover:border-amber-500/40 active:cursor-grabbing"
        draggable="true"
        @dragstart="onDragStart($event, node.type, node.label)"
      >
        <component :is="node.icon" class="h-4 w-4 shrink-0 text-amber-500" />
        <div class="min-w-0">
          <span class="block text-sm font-medium leading-tight">{{ node.label }}</span>
          <span class="block text-[10px] leading-tight text-muted-foreground">{{ node.desc }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>
