<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRoute } from 'vue-router'
import type { Node } from '@vue-flow/core'
import { X, Trash2 } from 'lucide-vue-next'
import { SLUG_TO_DEFINITION, FALLBACK_ICONS } from '@/features/workflows/registry'
import type { NodeCategory } from '@/features/workflows/registry'
import { nodeConfigComponents, ConnectionRequiredConfig, FallbackConfig } from './config'

const props = defineProps<{
  node: Node
}>()

const emit = defineEmits<{
  close: []
  updateConfig: [nodeId: string, config: Record<string, unknown>]
  removeNode: [nodeId: string]
}>()

// routing

const route = useRoute()
const workspaceId = computed(() => route.params.workspaceId as string)

// computed

const CATEGORY_COLOR: Record<NodeCategory, string> = { trigger: 'emerald', action: 'blue', logic: 'amber' }

const nodeInfo = computed(() => {
  const type = (props.node.data?.nodeType as string) ?? props.node.type
  const def = SLUG_TO_DEFINITION[type]
  const category: NodeCategory = def?.category ?? 'action'
  return {
    type,
    label: (props.node.data?.label as string) ?? def?.label ?? type,
    config: (props.node.data?.config as Record<string, unknown>) ?? {},
    needsConnection: def?.requiresConnection ?? false,
    category,
    categoryColor: CATEGORY_COLOR[category],
    icon: def?.icon ?? FALLBACK_ICONS[category],
  }
})

const configComponent = computed<Component>(() => {
  const type = nodeInfo.value.type
  if (type in nodeConfigComponents) return nodeConfigComponents[type]
  if (nodeInfo.value.needsConnection) return ConnectionRequiredConfig
  return FallbackConfig
})

// actions

function updateField(key: string, value: unknown) {
  emit('updateConfig', props.node.id, { ...nodeInfo.value.config, [key]: value })
}
</script>

<template>
  <aside class="flex w-80 flex-col border-l bg-background">
    <!-- header -->
    <div class="flex items-center gap-3 border-b px-4 py-3">
      <div
        class="rounded-md p-1.5"
        :class="{
          'bg-emerald-500/10': nodeInfo.categoryColor === 'emerald',
          'bg-blue-500/10': nodeInfo.categoryColor === 'blue',
          'bg-amber-500/10': nodeInfo.categoryColor === 'amber',
        }"
      >
        <component
          :is="nodeInfo.icon"
          class="h-4 w-4"
          :class="{
            'text-emerald-500': nodeInfo.categoryColor === 'emerald',
            'text-blue-500': nodeInfo.categoryColor === 'blue',
            'text-amber-500': nodeInfo.categoryColor === 'amber',
          }"
        />
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-sm font-medium truncate">{{ nodeInfo.label }}</h3>
        <p class="text-[10px] text-muted-foreground capitalize">{{ nodeInfo.category }}</p>
      </div>
      <button
        class="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        @click="emit('close')"
      >
        <X class="h-4 w-4" />
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <component
        :is="configComponent"
        :config="nodeInfo.config"
        :workspace-id="workspaceId"
        :node-type="nodeInfo.type"
        @update-field="updateField"
      />

      <!-- footer -->
      <div class="border-t px-4 py-3 space-y-3">
        <button
          class="flex w-full items-center justify-center gap-1.5 rounded-md border border-destructive/30 px-3 py-2 text-xs font-medium text-destructive transition-colors hover:bg-destructive hover:text-destructive-foreground"
          @click="emit('removeNode', node.id)"
        >
          <Trash2 class="h-3.5 w-3.5" />
          Remove node
        </button>
        <p class="text-[10px] text-muted-foreground">
          ID: <code class="rounded bg-muted px-1 py-0.5 font-mono">{{ node.id }}</code>
        </p>
      </div>
    </div>
  </aside>
</template>
