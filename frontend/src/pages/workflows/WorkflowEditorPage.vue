<script setup lang="ts">
// @ts-nocheck — VueFlow generics cause TS2589 deep recursion with vue-tsc
import { computed, ref } from 'vue'
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
import { useExecutionList, useExecutionDetail } from '@/composables/useExecutions'
import { buildVueFlowNodeTypes } from '@/features/workflows/registry'
import {
  ArrowLeft, Save, Check, Loader2, Cloud, CloudOff, Play,
  CheckCircle, XCircle, ChevronDown, ChevronUp, Clock,
  SkipForward, History, AlertCircle,
} from 'lucide-vue-next'
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
  isRunning,
  runResult,
  runError,
  goBack,
  startEditName,
  finishEditName,
  saveWorkflow,
  executeRun,
  onNodeClick,
  onPaneClick,
  onDrop,
  onDragOver,
  handleUpdateConfig,
  handleRemoveNode,
} = useWorkflowEditor(workspaceId, workflowId)

// execution history

const { data: executionHistory } = useExecutionList(workspaceId, workflowId)
const selectedExecutionId = ref<string | null>(null)
const { data: executionDetail } = useExecutionDetail(workspaceId, selectedExecutionId)

// ui state

const showRunResults = ref(false)
const bottomTab = ref<'results' | 'history'>('results')

function navigateBack() {
  goBack()
  router.push({ name: 'workflows', params: { workspaceId: workspaceId.value } })
}

function viewExecution(executionId: string) {
  selectedExecutionId.value = executionId
  bottomTab.value = 'results'
  showRunResults.value = true
}

// computed: active execution display — latest run or a selected past execution
const activeExecution = computed(() => {
  const showingLatestRun = bottomTab.value === 'results'

  if (showingLatestRun && runResult.value) {
    return {
      nodes: runResult.value.node_results.map((nr) => ({
        node_id: nr.node_id,
        node_type: '',
        status: nr.status,
        output_data: nr.output,
        error: nr.error,
        duration_ms: nr.duration_ms,
      })),
      status: runResult.value.status as string | null,
      error: runError.value,
    }
  }

  if (executionDetail.value) {
    return {
      nodes: executionDetail.value.nodes.map((n) => ({
        node_id: n.node_id,
        node_type: n.node_type,
        status: n.status,
        output_data: n.output_data,
        error: n.error,
        duration_ms: n.duration_ms,
      })),
      status: executionDetail.value.status as string | null,
      error: executionDetail.value.error,
    }
  }

  return { nodes: [] as any[], status: null as string | null, error: runError.value }
})

function statusIcon(status: string) {
  if (status === 'completed') return CheckCircle
  if (status === 'failed') return XCircle
  if (status === 'running') return Loader2
  if (status === 'skipped') return SkipForward
  return Clock
}

function statusColor(status: string) {
  if (status === 'completed') return 'text-emerald-500'
  if (status === 'failed') return 'text-destructive'
  if (status === 'running') return 'text-blue-500'
  if (status === 'skipped') return 'text-muted-foreground'
  return 'text-amber-500'
}

function formatTime(iso: string | null) {
  if (!iso) return '-'
  return new Date(iso).toLocaleTimeString()
}

const hasBottomPanel = computed(() =>
  !!(runResult.value || runError.value || executionHistory.value?.length),
)
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

      <div class="flex items-center gap-2">
        <UiButton
          size="sm"
          variant="outline"
          :disabled="autoSaveStatus === 'saving'"
          @click="saveWorkflow"
        >
          <Loader2 v-if="autoSaveStatus === 'saving'" class="mr-1 h-4 w-4 animate-spin" />
          <Check v-else-if="autoSaveStatus === 'saved'" class="mr-1 h-4 w-4 text-emerald-500" />
          <Save v-else class="mr-1 h-4 w-4" />
          {{ autoSaveStatus === 'saved' ? 'Saved' : 'Save' }}
        </UiButton>
        <UiButton
          size="sm"
          :disabled="isRunning"
          @click="executeRun().then(() => { showRunResults = true; bottomTab = 'results'; selectedExecutionId = null })"
        >
          <Loader2 v-if="isRunning" class="mr-1 h-4 w-4 animate-spin" />
          <Play v-else class="mr-1 h-4 w-4" />
          {{ isRunning ? 'Running...' : 'Run' }}
        </UiButton>
      </div>
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

    <!-- bottom panel: execution results + history -->
    <div v-if="hasBottomPanel" class="border-t bg-background">
      <!-- tab bar + collapse toggle -->
      <div class="flex items-center justify-between border-b px-2">
        <div class="flex">
          <button
            :class="[
              'px-3 py-1.5 text-xs font-medium transition-colors',
              bottomTab === 'results'
                ? 'border-b-2 border-primary text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="bottomTab = 'results'; showRunResults = true"
          >
            <span class="flex items-center gap-1.5">
              <Play class="h-3 w-3" />
              Run Results
            </span>
          </button>
          <button
            :class="[
              'px-3 py-1.5 text-xs font-medium transition-colors',
              bottomTab === 'history'
                ? 'border-b-2 border-primary text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="bottomTab = 'history'; showRunResults = true"
          >
            <span class="flex items-center gap-1.5">
              <History class="h-3 w-3" />
              History
              <span
                v-if="executionHistory?.length"
                class="rounded-full bg-muted px-1.5 py-0.5 text-[10px]"
              >
                {{ executionHistory.length }}
              </span>
            </span>
          </button>
        </div>
        <button
          class="p-1.5 text-muted-foreground hover:text-foreground"
          @click="showRunResults = !showRunResults"
        >
          <ChevronUp v-if="showRunResults" class="h-3.5 w-3.5" />
          <ChevronDown v-else class="h-3.5 w-3.5" />
        </button>
      </div>

      <div v-if="showRunResults" class="max-h-64 overflow-y-auto">
        <!-- results tab: per-node step tracker -->
        <div v-if="bottomTab === 'results'" class="px-4 py-3 space-y-2">
          <div v-if="activeExecution.error && !activeExecution.nodes.length" class="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle class="h-4 w-4 shrink-0" />
            {{ activeExecution.error }}
          </div>

          <div v-if="activeExecution.status" class="flex items-center gap-2 mb-3">
            <component
              :is="statusIcon(activeExecution.status)"
              :class="['h-4 w-4', statusColor(activeExecution.status), activeExecution.status === 'running' ? 'animate-spin' : '']"
            />
            <span class="text-sm font-medium capitalize">{{ activeExecution.status }}</span>
          </div>

          <!-- step progress -->
          <div v-if="activeExecution.nodes.length" class="relative pl-6">
            <!-- vertical connector line -->
            <div class="absolute left-[11px] top-2 bottom-2 w-px bg-border" />

            <div
              v-for="(step, idx) in activeExecution.nodes"
              :key="step.node_id"
              class="relative mb-3 last:mb-0"
            >
              <!-- status dot on the connector line -->
              <div
                :class="[
                  'absolute -left-6 top-1 flex h-5 w-5 items-center justify-center rounded-full border-2 bg-background',
                  step.status === 'completed' ? 'border-emerald-500' : '',
                  step.status === 'failed' ? 'border-destructive' : '',
                  step.status === 'running' ? 'border-blue-500' : '',
                  step.status === 'skipped' ? 'border-muted-foreground' : '',
                  step.status === 'pending' ? 'border-amber-500' : '',
                ]"
              >
                <component
                  :is="statusIcon(step.status)"
                  :class="[
                    'h-3 w-3',
                    statusColor(step.status),
                    step.status === 'running' ? 'animate-spin' : '',
                  ]"
                />
              </div>

              <!-- step content -->
              <div class="rounded-md border p-3">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-mono text-muted-foreground">{{ idx + 1 }}</span>
                    <span class="text-sm font-medium">{{ step.node_id }}</span>
                    <span v-if="step.node_type" class="text-xs text-muted-foreground">{{ step.node_type }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span :class="['text-xs font-medium capitalize', statusColor(step.status)]">
                      {{ step.status }}
                    </span>
                    <span v-if="step.duration_ms > 0" class="text-xs text-muted-foreground">
                      {{ step.duration_ms }}ms
                    </span>
                  </div>
                </div>

                <p v-if="step.error" class="mt-2 rounded bg-destructive/10 px-2 py-1 text-xs text-destructive">
                  {{ step.error }}
                </p>

                <details
                  v-if="step.output_data && Object.keys(step.output_data).length > 0"
                  class="mt-2"
                >
                  <summary class="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                    Output
                  </summary>
                  <pre class="mt-1 max-h-24 overflow-auto rounded bg-muted p-2 text-[11px] font-mono">{{ JSON.stringify(step.output_data, null, 2) }}</pre>
                </details>
              </div>
            </div>
          </div>

          <div
            v-if="!activeExecution.nodes.length && !activeExecution.error"
            class="text-center text-sm text-muted-foreground py-6"
          >
            Run a workflow to see step-by-step results here.
          </div>
        </div>

        <!-- history tab: past executions list -->
        <div v-if="bottomTab === 'history'" class="px-4 py-3">
          <div
            v-if="!executionHistory?.length"
            class="text-center text-sm text-muted-foreground py-6"
          >
            No execution history yet. Click Run to test your workflow.
          </div>

          <div v-else class="space-y-1">
            <button
              v-for="exec in executionHistory"
              :key="exec.id"
              :class="[
                'flex w-full items-center justify-between rounded-md border px-3 py-2 text-left text-sm transition-colors',
                selectedExecutionId === exec.id
                  ? 'border-primary bg-primary/5'
                  : 'hover:border-primary/40',
              ]"
              @click="viewExecution(exec.id)"
            >
              <div class="flex items-center gap-2">
                <component
                  :is="statusIcon(exec.status)"
                  :class="['h-3.5 w-3.5', statusColor(exec.status)]"
                />
                <span class="font-medium capitalize">{{ exec.status }}</span>
              </div>
              <span class="text-xs text-muted-foreground">
                {{ formatTime(exec.started_at) }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
