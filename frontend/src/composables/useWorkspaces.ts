import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { Ref } from 'vue'
import type { WorkspaceUpdateBody } from '@/types/workspace'
import {
  listWorkspaces,
  createWorkspace,
  updateWorkspace,
  deleteWorkspace,
} from '@/services/api/workspaces'
import { useWorkspaceStore } from '@/stores/workspace'

// queries

// Fetches all workspaces the user belongs to.
// TanStack Query caches the result and refetches automatically when the data
// goes stale (e.g. after a mutation invalidates it), so every component that
// calls this shares the same up-to-date list without manual coordination.
export function useWorkspacesQuery() {
  return useQuery({
    queryKey: ['workspaces'],
    queryFn: () => listWorkspaces(),
  })
}

// mutations

// Creates a new workspace, then tells TanStack Query to refetch the workspace
// list so the UI stays in sync without a full page reload.
export function useCreateWorkspace() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: { name: string; slug: string }) =>
      createWorkspace(vars.name, vars.slug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
    },
  })
}

// Updates a workspace (name, theme, etc.), refetches the list, and keeps the
// workspace store's "current" pointer in sync if it's the active workspace.
export function useUpdateWorkspace() {
  const queryClient = useQueryClient()
  const store = useWorkspaceStore()
  return useMutation({
    mutationFn: (vars: { workspaceId: string; body: WorkspaceUpdateBody }) =>
      updateWorkspace(vars.workspaceId, vars.body),
    onSuccess: (updatedWorkspace) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      if (store.current?.id === updatedWorkspace.id) {
        store.selectWorkspace(updatedWorkspace)
      }
    },
  })
}

// Permanently deletes a workspace, clears it from the store if it was active,
// and refetches the list.
export function useDeleteWorkspace() {
  const queryClient = useQueryClient()
  const store = useWorkspaceStore()
  return useMutation({
    mutationFn: (workspaceId: string) => deleteWorkspace(workspaceId),
    onSuccess: (_data, deletedWorkspaceId) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      if (store.current?.id === deletedWorkspaceId) {
        store.clear()
      }
    },
  })
}
