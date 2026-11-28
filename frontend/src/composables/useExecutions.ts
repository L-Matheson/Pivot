import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { listExecutions, getExecution } from '@/services/api/executions'
import type { ExecutionListItem, ExecutionDetail } from '@/types/execution'

export function useExecutionList(workspaceId: Ref<string>, workflowId: Ref<string>) {
  return useQuery<ExecutionListItem[]>({
    queryKey: computed(() => ['executions', workspaceId.value, workflowId.value]),
    queryFn: () => listExecutions(workspaceId.value, workflowId.value),
    enabled: computed(() => !!workspaceId.value && !!workflowId.value),
  })
}

export function useExecutionDetail(workspaceId: Ref<string>, executionId: Ref<string | null>) {
  return useQuery<ExecutionDetail>({
    queryKey: computed(() => ['execution', workspaceId.value, executionId.value]),
    queryFn: () => getExecution(workspaceId.value, executionId.value!),
    enabled: computed(() => !!workspaceId.value && !!executionId.value),
  })
}
