<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/services/api'
import UiButton from '@/components/ui/button.vue'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiCard from '@/components/ui/card.vue'
import UiSpinner from '@/components/ui/spinner.vue'
import { Workflow } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const displayName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }

  submitting.value = true
  try {
    await auth.register(email.value, password.value, displayName.value)
    router.push('/workspaces')
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
        <h1 class="text-xl font-semibold tracking-tight">Get started</h1>
        <p class="mt-1 text-sm text-muted-foreground">Create your Pivot account</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="space-y-2">
          <UiLabel for="displayName">Name</UiLabel>
          <UiInput
            id="displayName"
            v-model="displayName"
            placeholder="Your name"
            required
          />
        </div>

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
            placeholder="At least 8 characters"
            required
          />
        </div>

        <div class="space-y-2">
          <UiLabel for="confirmPassword">Confirm password</UiLabel>
          <UiInput
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Repeat your password"
            required
          />
        </div>

        <p v-if="error" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {{ error }}
        </p>

        <UiButton class="w-full" :disabled="submitting">
          <UiSpinner v-if="submitting" class="h-4 w-4" />
          <span v-else>Create account</span>
        </UiButton>
      </form>

      <p class="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?
        <RouterLink to="/login" class="font-medium text-primary hover:underline">
          Sign in
        </RouterLink>
      </p>
    </UiCard>
  </div>
</template>
