<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOAuthCallback } from '@/composables/useConnections'
import UiSpinner from '@/components/ui/spinner.vue'

// routing

const route = useRoute()
const router = useRouter()
const workspaceId = ref(route.params.workspaceId as string)
const provider = ref(route.params.provider as string)

// data

const callbackMutation = useOAuthCallback(workspaceId)
const errorMessage = ref('')

// actions

onMounted(async () => {
  const code = route.query.code as string | undefined
  const state = route.query.state as string | undefined

  if (!code || !state) {
    errorMessage.value = 'Missing authorization code or state parameter.'
    return
  }

  try {
    await callbackMutation.mutateAsync({
      provider: provider.value,
      code,
      state,
    })
    router.replace({ name: 'connections', params: { workspaceId: workspaceId.value } })
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Failed to complete authorization.'
    errorMessage.value = message
  }
})
</script>

<template>
  <div class="flex h-full items-center justify-center p-8">
    <div v-if="errorMessage" class="text-center">
      <p class="text-sm font-medium text-destructive">{{ errorMessage }}</p>
      <button
        class="mt-4 text-sm text-primary underline"
        @click="router.push({ name: 'connections', params: { workspaceId } })"
      >
        Back to Connections
      </button>
    </div>

    <div v-else class="flex flex-col items-center gap-3">
      <UiSpinner class="h-6 w-6" />
      <p class="text-sm text-muted-foreground">Completing authorization&hellip;</p>
    </div>
  </div>
</template>
