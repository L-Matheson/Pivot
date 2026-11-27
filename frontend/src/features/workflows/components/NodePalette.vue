<script setup lang="ts">
import { HelpCircle } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { nodesByCategory, CATEGORY_COLORS, type NodeDefinition } from '@/features/workflows/registry'

// routing

const route = useRoute()
const workspaceId = route.params.workspaceId as string

// node definitions — derived from the registry

const triggerNodes = nodesByCategory('trigger')
const actionNodes = nodesByCategory('action')
const logicNodes = nodesByCategory('logic')

// drag handlers

function onDragStart(event: DragEvent, node: NodeDefinition) {
  if (!event.dataTransfer) return
  event.dataTransfer.setData('application/pivot-node-type', node.component)
  event.dataTransfer.setData('application/pivot-node-label', node.label)
  event.dataTransfer.setData('application/pivot-node-slug', node.slug)
  event.dataTransfer.effectAllowed = 'move'
}
</script>

<template>
  <aside class="w-64 overflow-y-auto border-r bg-sidebar p-4">
    <div class="mb-3 flex items-center justify-between">
      <p class="text-xs font-medium text-muted-foreground">Nodes</p>
      <RouterLink
        :to="{ name: 'workflow-help', params: { workspaceId } }"
        class="flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
      >
        <HelpCircle class="h-3 w-3" />
        Help
      </RouterLink>
    </div>

    <p class="mb-2 text-xs font-medium text-emerald-600 dark:text-emerald-400">Triggers</p>
    <div class="space-y-1">
      <div
        v-for="node in triggerNodes"
        :key="node.slug"
        class="flex cursor-grab items-center gap-2.5 rounded-md border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 transition-colors hover:border-emerald-500/40 active:cursor-grabbing"
        draggable="true"
        @dragstart="onDragStart($event, node)"
      >
        <component :is="node.icon" class="h-4 w-4 shrink-0 text-emerald-500" />
        <div class="min-w-0">
          <span class="block text-sm font-medium leading-tight">{{ node.label }}</span>
          <span class="block text-[10px] leading-tight text-muted-foreground">{{ node.description }}</span>
        </div>
      </div>
    </div>

    <div class="my-3 h-px bg-border" />

    <p class="mb-2 text-xs font-medium text-blue-600 dark:text-blue-400">Actions</p>
    <div class="space-y-1">
      <div
        v-for="node in actionNodes"
        :key="node.slug"
        class="flex cursor-grab items-center gap-2.5 rounded-md border border-blue-500/20 bg-blue-500/5 px-3 py-2 transition-colors hover:border-blue-500/40 active:cursor-grabbing"
        draggable="true"
        @dragstart="onDragStart($event, node)"
      >
        <component :is="node.icon" class="h-4 w-4 shrink-0 text-blue-500" />
        <div class="min-w-0">
          <span class="block text-sm font-medium leading-tight">{{ node.label }}</span>
          <span class="block text-[10px] leading-tight text-muted-foreground">{{ node.description }}</span>
        </div>
      </div>
    </div>

    <div class="my-3 h-px bg-border" />

    <p class="mb-2 text-xs font-medium text-amber-600 dark:text-amber-400">Logic</p>
    <div class="space-y-1">
      <div
        v-for="node in logicNodes"
        :key="node.slug"
        class="flex cursor-grab items-center gap-2.5 rounded-md border border-amber-500/20 bg-amber-500/5 px-3 py-2 transition-colors hover:border-amber-500/40 active:cursor-grabbing"
        draggable="true"
        @dragstart="onDragStart($event, node)"
      >
        <component :is="node.icon" class="h-4 w-4 shrink-0 text-amber-500" />
        <div class="min-w-0">
          <span class="block text-sm font-medium leading-tight">{{ node.label }}</span>
          <span class="block text-[10px] leading-tight text-muted-foreground">{{ node.description }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>
