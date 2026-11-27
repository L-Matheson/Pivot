import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserRead } from '@/types/auth'
import { login as apiLogin, register as apiRegister, getMe, logout as apiLogout } from '@/services/api/auth'
import { setAccessToken, clearAccessToken, refreshAccessToken } from '@/services/api/client'

export const useAuthStore = defineStore('auth', () => {
  // state

  const user = ref<UserRead | null>(null)
  const isLoading = ref(false)
  const initializing = ref(true)

  const isAuthenticated = computed(() => user.value !== null)

  // auth actions

  async function login(email: string, password: string) {
    const tokens = await apiLogin(email, password)
    setAccessToken(tokens.access_token, tokens.expires_in)
    await fetchUser()
  }

  async function register(email: string, password: string, displayName: string) {
    await apiRegister(email, password, displayName)
    await login(email, password)
  }

  async function fetchUser() {
    isLoading.value = true
    try {
      user.value = await getMe()
    } catch {
      user.value = null
      clearAccessToken()
    } finally {
      isLoading.value = false
      initializing.value = false
    }
  }

  async function restoreSession() {
    isLoading.value = true
    try {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        user.value = await getMe()
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    } finally {
      isLoading.value = false
      initializing.value = false
    }
  }

  async function logout() {
    try {
      await apiLogout()
    } catch {
      // Clear client state even if the server call fails
    }
    clearAccessToken()
    user.value = null
  }

  return { user, isLoading, initializing, isAuthenticated, login, register, fetchUser, restoreSession, logout }
})
