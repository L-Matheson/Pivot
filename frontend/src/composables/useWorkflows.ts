import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import type { WorkflowDefinition } from '@/types/workflow'
import {
  listWorkflows,
  createWorkflow,
  getWorkflow,
  updateWorkflow,
  duplicateWorkflow,
  archiveWorkflow,
  deleteWorkflow,
} from '@/services/api/workflows'

// queries

export function useWorkflowList(workspaceId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ['workflows', workspaceId.value]),
    queryFn: () => listWorkflows(workspaceId.value),
  })
}

export function useWorkflow(workspaceId: Ref<string>, workflowId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ['workflow', workspaceId.value, workflowId.value]),
    queryFn: () => getWorkflow(workspaceId.value, workflowId.value),
  })
}

// mutations

export function useCreateWorkflow(workspaceId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: { name: string; description?: string }) =>
      createWorkflow(workspaceId.value, vars),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows', workspaceId.value] })
    },
  })
}

export function useUpdateWorkflow(workspaceId: Ref<string>, workflowId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: {
      name?: string
      description?: string
      folder?: string
      tags?: string[]
      definition?: WorkflowDefinition
      is_active?: boolean
    }) => updateWorkflow(workspaceId.value, workflowId.value, vars),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows', workspaceId.value] })
      queryClient.invalidateQueries({
        queryKey: ['workflow', workspaceId.value, workflowId.value],
      })
    },
  })
}

export function useDuplicateWorkflow(workspaceId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (workflowId: string) => duplicateWorkflow(workspaceId.value, workflowId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows', workspaceId.value] })
    },
  })
}

export function useArchiveWorkflow(workspaceId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (workflowId: string) => archiveWorkflow(workspaceId.value, workflowId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows', workspaceId.value] })
    },
  })
}

export function useDeleteWorkflow(workspaceId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (workflowId: string) => deleteWorkflow(workspaceId.value, workflowId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows', workspaceId.value] })
    },
  })
}
