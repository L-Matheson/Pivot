import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getMe, login as apiLogin, register as apiRegister, type UserRead } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserRead | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!localStorage.getItem('access_token'))

  async function login(email: string, password: string) {
    const tokens = await apiLogin(email, password)
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    await fetchUser()
  }

  async function register(email: string, password: string, displayName: string) {
    await apiRegister(email, password, displayName)
    await login(email, password)
  }

  async function fetchUser() {
    if (!localStorage.getItem('access_token')) return
    loading.value = true
    try {
      user.value = await getMe()
    } catch {
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, loading, isAuthenticated, login, register, fetchUser, logout }
})
