import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { getMe } from '@/services/api/auth'
import { useAuthStore } from '@/stores/auth'

export function useCurrentUser() {
  const authStore = useAuthStore()
  const isAuthenticated = computed(() => authStore.isAuthenticated)

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => getMe(),
    enabled: isAuthenticated,
  })
}
