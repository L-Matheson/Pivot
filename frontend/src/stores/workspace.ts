import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listWorkspaces,
  createWorkspace as apiCreateWorkspace,
  updateWorkspace as apiUpdateWorkspace,
  deleteWorkspace as apiDeleteWorkspace,
  type WorkspaceRead,
  type WorkspaceUpdateBody,
} from '@/services/api'

export const useWorkspaceStore = defineStore('workspace', () => {
  const workspaces = ref<WorkspaceRead[]>([])
  const current = ref<WorkspaceRead | null>(null)
  const loading = ref(false)

  async function fetchWorkspaces() {
    loading.value = true
    try {
      workspaces.value = await listWorkspaces()
    } finally {
      loading.value = false
    }
  }

  async function createWorkspace(name: string, slug: string) {
    const ws = await apiCreateWorkspace(name, slug)
    workspaces.value.push(ws)
    return ws
  }

  async function updateWorkspace(workspaceId: string, body: WorkspaceUpdateBody) {
    const ws = await apiUpdateWorkspace(workspaceId, body)
    const idx = workspaces.value.findIndex((w) => w.id === workspaceId)
    if (idx !== -1) workspaces.value[idx] = ws
    if (current.value?.id === workspaceId) current.value = ws
    return ws
  }

  async function removeWorkspace(workspaceId: string) {
    await apiDeleteWorkspace(workspaceId)
    workspaces.value = workspaces.value.filter((w) => w.id !== workspaceId)
    if (current.value?.id === workspaceId) {
      current.value = null
      localStorage.removeItem('current_workspace_id')
    }
  }

  function selectWorkspace(workspace: WorkspaceRead) {
    current.value = workspace
    localStorage.setItem('current_workspace_id', workspace.id)
  }

  function restoreWorkspace() {
    const savedId = localStorage.getItem('current_workspace_id')
    if (savedId && workspaces.value.length > 0) {
      const found = workspaces.value.find((ws) => ws.id === savedId)
      if (found) {
        current.value = found
        return
      }
    }
    if (workspaces.value.length === 1) {
      selectWorkspace(workspaces.value[0])
    }
  }

  function clear() {
    workspaces.value = []
    current.value = null
    localStorage.removeItem('current_workspace_id')
  }

  return {
    workspaces,
    current,
    loading,
    fetchWorkspaces,
    createWorkspace,
    updateWorkspace,
    removeWorkspace,
    selectWorkspace,
    restoreWorkspace,
    clear,
  }
})
