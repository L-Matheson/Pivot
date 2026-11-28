import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import {
  listConnections,
  deleteConnection,
  testConnection,
  oauthAuthorize,
  oauthCallback,
} from '@/services/api/connections'

// queries

export function useConnectionList(workspaceId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ['connections', workspaceId.value]),
    queryFn: () => listConnections(workspaceId.value),
  })
}

// mutations

export function useDeleteConnection(workspaceId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (connectionId: string) =>
      deleteConnection(workspaceId.value, connectionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections', workspaceId.value] })
    },
  })
}

export function useTestConnection(workspaceId: Ref<string>) {
  return useMutation({
    mutationFn: (connectionId: string) =>
      testConnection(workspaceId.value, connectionId),
  })
}

export function useOAuthAuthorize(workspaceId: Ref<string>) {
  return useMutation({
    mutationFn: (provider: string) =>
      oauthAuthorize(workspaceId.value, provider),
  })
}

export function useOAuthCallback(workspaceId: Ref<string>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: { provider: string; code: string; state: string }) =>
      oauthCallback(workspaceId.value, vars.provider, {
        code: vars.code,
        state: vars.state,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections', workspaceId.value] })
    },
  })
}
