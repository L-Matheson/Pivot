<script setup lang="ts">
// @ts-nocheck — VueFlow generics cause TS2589 deep recursion with vue-tsc
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VueFlow } from '@vue-flow/core'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import { Background } from '@vue-flow/background'
import NodePalette from '@/features/workflows/components/NodePalette.vue'
import NodeConfigPanel from '@/features/workflows/components/NodeConfigPanel.vue'
import UiButton from '@/components/ui/button.vue'
import UiInput from '@/components/ui/input.vue'
import { useTheme } from '@/composables/useTheme'
import { useWorkflowEditor } from '@/composables/useWorkflowEditor'
import { buildVueFlowNodeTypes } from '@/features/workflows/registry'
import { ArrowLeft, Save, Check, Loader2, Cloud, CloudOff } from 'lucide-vue-next'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/minimap/dist/style.css'
import '@vue-flow/controls/dist/style.css'

// routing

const route = useRoute()
const router = useRouter()
const workspaceId = computed(() => route.params.workspaceId as string)
const workflowId = computed(() => route.params.workflowId as string)

// canvas configuration

const { isDark } = useTheme()
const backgroundDotColor = computed(() => (isDark.value ? '#1a1a2e' : '#aaaaaa'))
const backgroundGap = 16
const nodeTypes = buildVueFlowNodeTypes()

// editor state + actions (extracted composable)

const {
  nodes,
  edges,
  isLoading,
  selectedNodeId,
  selectedNode,
  editingName,
  workflowName,
  autoSaveStatus,
  goBack,
  startEditName,
  finishEditName,
  saveWorkflow,
  onNodeClick,
  onPaneClick,
  onDrop,
  onDragOver,
  handleUpdateConfig,
  handleRemoveNode,
} = useWorkflowEditor(workspaceId, workflowId)

function navigateBack() {
  goBack()
  router.push({ name: 'workflows', params: { workspaceId: workspaceId.value } })
}
</script>

<template>
  <div class="flex h-full flex-col">
    <header class="flex items-center justify-between border-b bg-background px-4 py-2">
      <div class="flex items-center gap-3">
        <UiButton variant="ghost" size="icon" @click="navigateBack">
          <ArrowLeft class="h-4 w-4" />
        </UiButton>

        <template v-if="editingName">
          <UiInput
            v-model="workflowName"
            class="h-7 w-56 text-sm font-medium"
            @keyup.enter="finishEditName"
            @blur="finishEditName"
            autofocus
          />
        </template>
        <button
          v-else
          class="text-sm font-medium hover:text-primary"
          @click="startEditName"
        >
          {{ workflowName || 'Untitled Workflow' }}
        </button>

        <!-- auto-save indicator -->
        <div class="flex items-center gap-1.5 text-[11px] text-muted-foreground">
          <template v-if="autoSaveStatus === 'saving'">
            <Loader2 class="h-3 w-3 animate-spin" />
            <span>Saving...</span>
          </template>
          <template v-else-if="autoSaveStatus === 'saved'">
            <Cloud class="h-3 w-3 text-emerald-500" />
            <span class="text-emerald-600 dark:text-emerald-400">Saved</span>
          </template>
          <template v-else-if="autoSaveStatus === 'error'">
            <CloudOff class="h-3 w-3 text-destructive" />
            <span class="text-destructive">Save failed</span>
          </template>
        </div>
      </div>

      <UiButton
        size="sm"
        :disabled="autoSaveStatus === 'saving'"
        @click="saveWorkflow"
      >
        <Loader2 v-if="autoSaveStatus === 'saving'" class="mr-1 h-4 w-4 animate-spin" />
        <Check v-else-if="autoSaveStatus === 'saved'" class="mr-1 h-4 w-4 text-emerald-500" />
        <Save v-else class="mr-1 h-4 w-4" />
        {{ autoSaveStatus === 'saved' ? 'Saved' : 'Save' }}
      </UiButton>
    </header>

    <div v-if="isLoading" class="flex flex-1 items-center justify-center">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>

    <div v-else class="flex flex-1 overflow-hidden">
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
          @node-click="onNodeClick"
          @pane-click="onPaneClick"
        >
          <Background :color="backgroundDotColor" :gap="backgroundGap" />
          <MiniMap />
          <Controls />
        </VueFlow>
      </div>

      <NodeConfigPanel
        v-if="selectedNode"
        :node="selectedNode"
        @close="selectedNodeId = null"
        @update-config="handleUpdateConfig"
        @remove-node="handleRemoveNode"
      />
    </div>
  </div>
</template>
