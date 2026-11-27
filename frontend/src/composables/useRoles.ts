import type { Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { listRoles } from '@/services/api/roles'

export function useRoleList(workspaceId: Ref<string>) {
  return useQuery({
    queryKey: ['roles', workspaceId],
    queryFn: () => listRoles(workspaceId.value),
    enabled: () => !!workspaceId.value,
  })
}
