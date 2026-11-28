// @ts-nocheck — VueFlow generics cause TS2589 deep recursion with vue-tsc
import { ref, computed, watch, type Ref } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { useWorkflow, useUpdateWorkflow } from '@/composables/useWorkflows'
import { runWorkflow } from '@/services/api/executions'
import { SLUG_TO_COMPONENT, SLUG_TO_LABEL } from '@/features/workflows/registry'
import type { WorkflowRunResponse } from '@/types/execution'

export type AutoSaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export function useWorkflowEditor(workspaceId: Ref<string>, workflowId: Ref<string>) {
  const queryClient = useQueryClient()
  const { data: workflow, isLoading } = useWorkflow(workspaceId, workflowId)
  const updateMutation = useUpdateWorkflow(workspaceId, workflowId)

  // graph state

  const nodes = ref<Node[]>([])
  const edges = ref<Edge[]>([])
  const loaded = ref(false)

  // selection — by ID so the reference never goes stale

  const selectedNodeId = ref<string | null>(null)
  const selectedNode = computed(() =>
    selectedNodeId.value ? nodes.value.find((n) => n.id === selectedNodeId.value) ?? null : null,
  )

  // name editing

  const editingName = ref(false)
  const workflowName = ref('')

  function startEditName() {
    editingName.value = true
  }

  function finishEditName() {
    editingName.value = false
    if (!workflowName.value.trim() && workflow.value) {
      workflowName.value = workflow.value.name
    }
    scheduleAutoSave()
  }

  // auto-save

  const autoSaveStatus = ref<AutoSaveStatus>('idle')
  let saveTimer: ReturnType<typeof setTimeout> | null = null
  let saveVersion = 0

  function buildDefinition() {
    return {
      schema_version: 1,
      nodes: nodes.value.map((n) => ({
        id: n.id,
        type: (n.data?.nodeType as string) ?? n.type,
        position: { x: n.position.x, y: n.position.y },
        config: (n.data?.config as Record<string, unknown>) ?? {},
      })),
      edges: edges.value.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        source_handle: e.sourceHandle ?? null,
      })),
    }
  }

  function scheduleAutoSave() {
    if (!loaded.value) return
    if (saveTimer) clearTimeout(saveTimer)
    autoSaveStatus.value = 'idle'
    saveTimer = setTimeout(() => doAutoSave(), 1500)
  }

  async function doAutoSave() {
    saveTimer = null
    const version = ++saveVersion
    autoSaveStatus.value = 'saving'
    try {
      await updateMutation.mutateAsync({
        name: workflowName.value,
        definition: buildDefinition(),
      })
      if (saveVersion === version) {
        autoSaveStatus.value = 'saved'
        setTimeout(() => {
          if (autoSaveStatus.value === 'saved') autoSaveStatus.value = 'idle'
        }, 3000)
      }
    } catch {
      if (saveVersion === version) {
        autoSaveStatus.value = 'error'
      }
    }
  }

  function flushSave() {
    if (saveTimer) {
      clearTimeout(saveTimer)
      saveTimer = null
      doAutoSave()
    }
  }

  async function saveWorkflow() {
    if (saveTimer) {
      clearTimeout(saveTimer)
      saveTimer = null
    }
    autoSaveStatus.value = 'saving'
    const version = ++saveVersion
    try {
      await updateMutation.mutateAsync({
        name: workflowName.value,
        definition: buildDefinition(),
      })
      if (saveVersion === version) {
        autoSaveStatus.value = 'saved'
        setTimeout(() => {
          if (autoSaveStatus.value === 'saved') autoSaveStatus.value = 'idle'
        }, 3000)
      }
    } catch {
      if (saveVersion === version) {
        autoSaveStatus.value = 'error'
      }
    }
  }

  // execution

  const isRunning = ref(false)
  const runResult = ref<WorkflowRunResponse | null>(null)
  const runError = ref<string | null>(null)

  async function executeRun() {
    flushSave()
    // wait for any in-flight save to complete
    if (autoSaveStatus.value === 'saving') {
      await new Promise<void>((resolve) => {
        const unwatch = watch(autoSaveStatus, (val) => {
          if (val !== 'saving') {
            unwatch()
            resolve()
          }
        })
      })
    }

    isRunning.value = true
    runResult.value = null
    runError.value = null
    try {
      runResult.value = await runWorkflow(workspaceId.value, workflowId.value)
      queryClient.invalidateQueries({ queryKey: ['executions', workspaceId.value, workflowId.value] })
    } catch (err: unknown) {
      runError.value = err instanceof Error ? err.message : 'Execution failed.'
    } finally {
      isRunning.value = false
    }
  }

  // vueflow event handlers

  const {
    onConnect,
    addEdges,
    onNodesChange,
    onEdgesChange,
    applyNodeChanges,
    applyEdgeChanges,
    project,
  } = useVueFlow()

  onNodesChange((changes) => applyNodeChanges(changes))
  onEdgesChange((changes) => applyEdgeChanges(changes))
  onConnect((params) => addEdges(params))

  // pane-click fires on the same DOM click as node-click when the event
  // propagates through the VueFlow container. Guard with a flag so pane-click
  // never stomps a node-click that just ran on the same tick.
  let nodeClickedThisTick = false

  function onNodeClick(nodeEvent: { event: MouseEvent; node: Node }) {
    selectedNodeId.value = nodeEvent.node.id
    nodeClickedThisTick = true
    requestAnimationFrame(() => { nodeClickedThisTick = false })
  }

  function onPaneClick() {
    if (nodeClickedThisTick) return
    selectedNodeId.value = null
  }

  function handleUpdateConfig(nodeId: string, config: Record<string, unknown>) {
    const node = nodes.value.find((n) => n.id === nodeId)
    if (node) {
      node.data = { ...node.data, config }
      scheduleAutoSave()
    }
  }

  function handleRemoveNode(nodeId: string) {
    if (selectedNodeId.value === nodeId) {
      selectedNodeId.value = null
    }
    edges.value = edges.value.filter(
      (e) => e.source !== nodeId && e.target !== nodeId,
    )
    nodes.value = nodes.value.filter((n) => n.id !== nodeId)
    scheduleAutoSave()
  }

  function onDrop(event: DragEvent) {
    const nodeType = event.dataTransfer?.getData('application/pivot-node-type')
    const nodeLabel = event.dataTransfer?.getData('application/pivot-node-label')
    const nodeSlug = event.dataTransfer?.getData('application/pivot-node-slug')
    if (!nodeType || !nodeLabel) return

    const flowContainer = document.querySelector('.vue-flow') as HTMLElement
    if (!flowContainer) return

    const bounds = flowContainer.getBoundingClientRect()
    const position = project({
      x: event.clientX - bounds.left,
      y: event.clientY - bounds.top,
    })

    const newNode: Node = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType,
      position,
      data: {
        label: nodeLabel,
        nodeType: nodeSlug ?? nodeType,
        config: {},
      },
    }
    nodes.value.push(newNode)
    selectedNodeId.value = newNode.id
    scheduleAutoSave()
  }

  function onDragOver(event: DragEvent) {
    event.preventDefault()
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move'
    }
  }

  // watchers

  watch(
    () => edges.value.length,
    (newLen, oldLen) => {
      if (loaded.value && newLen !== oldLen) scheduleAutoSave()
    },
  )

  watch(
    () => nodes.value.map((n) => `${n.id}:${Math.round(n.position.x)},${Math.round(n.position.y)}`).join('|'),
    () => {
      if (loaded.value) scheduleAutoSave()
    },
  )

  watch(
    () => workflow.value,
    (wf) => {
      if (!wf || loaded.value) return
      workflowName.value = wf.name

      const def = wf.definition
      if (def?.nodes?.length) {
        nodes.value = def.nodes.map((n: any) => ({
          id: n.id,
          type: SLUG_TO_COMPONENT[n.type] ?? 'action',
          position: { x: n.position.x, y: n.position.y },
          data: {
            label: SLUG_TO_LABEL[n.type] ?? n.type,
            nodeType: n.type,
            config: n.config ?? {},
          },
        }))
      }
      if (def?.edges?.length) {
        edges.value = def.edges.map((e: any) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          sourceHandle: e.source_handle ?? undefined,
        }))
      }
      loaded.value = true
    },
    { immediate: true },
  )

  return {
    // state
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
    // actions
    goBack: flushSave,
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
  }
}
