import { useQuery } from '@tanstack/vue-query'
import { listPermissions } from '@/services/api/permissions'

export function usePermissionCatalog() {
  return useQuery({
    queryKey: ['permissions'],
    queryFn: () => listPermissions(),
    staleTime: Infinity,
  })
}
