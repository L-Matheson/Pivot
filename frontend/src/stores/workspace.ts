import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WorkspaceRead } from '@/types/workspace'

// Tracks which workspace the user is currently working in.
// Data fetching (list, create, update, delete) is handled by the useWorkspaces composable
// via TanStack Query — this store only manages the "current workspace" selection state.
export const useWorkspaceStore = defineStore('workspace', () => {
  // state

  const current = ref<WorkspaceRead | null>(null)

  // actions

  function selectWorkspace(workspace: WorkspaceRead) {
    current.value = workspace
    localStorage.setItem('current_workspace_id', workspace.id)
  }

  function restoreFromList(workspaces: WorkspaceRead[]) {
    const savedId = localStorage.getItem('current_workspace_id')
    if (savedId) {
      const matchingWorkspace = workspaces.find((workspace) => workspace.id === savedId)
      if (matchingWorkspace) {
        current.value = matchingWorkspace
        return
      }
    }
    if (workspaces.length === 1) {
      selectWorkspace(workspaces[0])
    }
  }

  function clear() {
    current.value = null
    localStorage.removeItem('current_workspace_id')
  }

  return { current, selectWorkspace, restoreFromList, clear }
})
