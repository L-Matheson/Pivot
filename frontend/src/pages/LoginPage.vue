<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/services/api'
import UiButton from '@/components/ui/button.vue'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiCard from '@/components/ui/card.vue'
import UiSpinner from '@/components/ui/spinner.vue'
import { Workflow } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = (route.query.redirect as string) ?? '/workspaces'
    router.push(redirect)
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail : 'An unexpected error occurred.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <UiCard class="w-full max-w-sm p-8">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
          <Workflow class="h-5 w-5 text-primary-foreground" />
        </div>
        <h1 class="text-xl font-semibold tracking-tight">Welcome back</h1>
        <p class="mt-1 text-sm text-muted-foreground">Sign in to your Pivot account</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="space-y-2">
          <UiLabel for="email">Email</UiLabel>
          <UiInput
            id="email"
            v-model="email"
            type="email"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="space-y-2">
          <UiLabel for="password">Password</UiLabel>
          <UiInput
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            required
          />
        </div>

        <p v-if="error" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {{ error }}
        </p>

        <UiButton class="w-full" :disabled="submitting">
          <UiSpinner v-if="submitting" class="h-4 w-4" />
          <span v-else>Sign in</span>
        </UiButton>
      </form>

      <p class="mt-6 text-center text-sm text-muted-foreground">
        Don't have an account?
        <RouterLink to="/register" class="font-medium text-primary hover:underline">
          Sign up
        </RouterLink>
      </p>
    </UiCard>
  </div>
</template>
