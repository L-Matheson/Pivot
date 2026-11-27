<script setup lang="ts">
// @ts-nocheck — VueFlow generics cause TS2589 deep recursion with vue-tsc
import { ref, markRaw, computed, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VueFlow, useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import { Background } from '@vue-flow/background'
import TriggerNode from '@/features/workflows/components/TriggerNode.vue'
import ActionNode from '@/features/workflows/components/ActionNode.vue'
import ConditionNode from '@/features/workflows/components/ConditionNode.vue'
import LoopNode from '@/features/workflows/components/LoopNode.vue'
import ParallelNode from '@/features/workflows/components/ParallelNode.vue'
import NodePalette from '@/features/workflows/components/NodePalette.vue'
import UiButton from '@/components/ui/button.vue'
import { useTheme } from '@/composables/useTheme'
import { ArrowLeft, Save } from 'lucide-vue-next'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/minimap/dist/style.css'
import '@vue-flow/controls/dist/style.css'

// routing

const route = useRoute()
const router = useRouter()
const workspaceId = route.params.workspaceId as string

// canvas configuration

const { isDark } = useTheme()
const backgroundDotColor = computed(() => (isDark.value ? '#1a1a2e' : '#aaaaaa'))
const backgroundGap = 16

// node type registry
// Maps each node type name to its Vue component so VueFlow renders the right one
const nodeTypes: Record<string, Component> = {
  trigger: markRaw(TriggerNode),
  action: markRaw(ActionNode),
  condition: markRaw(ConditionNode),
  loop: markRaw(LoopNode),
  parallel: markRaw(ParallelNode),
}

// graph state

const nodes = ref<Node[]>([
  {
    id: 'trigger-1',
    type: 'trigger',
    position: { x: 250, y: 50 },
    data: { label: 'Email Received', icon: 'mail' },
  },
])

const edges = ref<Edge[]>([])

// vueflow event handlers

const { onConnect, addEdges, onNodesChange, onEdgesChange, applyNodeChanges, applyEdgeChanges } =
  useVueFlow()

onNodesChange((changes) => applyNodeChanges(changes))
onEdgesChange((changes) => applyEdgeChanges(changes))
onConnect((params) => addEdges(params))

// drag and drop

function onDrop(event: DragEvent) {
  const nodeType = event.dataTransfer?.getData('application/pivot-node-type')
  const nodeLabel = event.dataTransfer?.getData('application/pivot-node-label')
  if (!nodeType || !nodeLabel) return

  const flowContainer = document.querySelector('.vue-flow') as HTMLElement
  if (!flowContainer) return

  const bounds = flowContainer.getBoundingClientRect()
  const position = {
    x: event.clientX - bounds.left,
    y: event.clientY - bounds.top,
  }

  const newNode: Node = {
    id: `${nodeType}-${Date.now()}`,
    type: nodeType,
    position,
    data: { label: nodeLabel },
  }
  nodes.value.push(newNode)
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

// actions

function goBack() {
  router.push({ name: 'workflows', params: { workspaceId } })
}
</script>

<template>
  <div class="flex h-full flex-col">
    <header class="flex items-center justify-between border-b bg-background px-4 py-2">
      <div class="flex items-center gap-3">
        <UiButton variant="ghost" size="icon" @click="goBack">
          <ArrowLeft class="h-4 w-4" />
        </UiButton>
        <h1 class="text-sm font-medium">Workflow Editor</h1>
      </div>
      <UiButton size="sm">
        <Save class="mr-1 h-4 w-4" />
        Save
      </UiButton>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <NodePalette />

      <div class="flex-1" @drop="onDrop" @dragover="onDragOver">
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes"
          :default-viewport="{ zoom: 1, x: 0, y: 0 }"
          :snap-to-grid="true"
          :snap-grid="[16, 16]"
          fit-view-on-init
          class="h-full"
        >
          <Background :color="backgroundDotColor" :gap="backgroundGap" />
          <MiniMap />
          <Controls />
        </VueFlow>
      </div>
    </div>
  </div>
</template>
