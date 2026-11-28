<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Unplug } from 'lucide-vue-next'

defineProps<{
  config: Record<string, unknown>
  workspaceId: string
  nodeType: string
}>()

defineEmits<{
  'update-field': [key: string, value: unknown]
}>()
</script>

<template>
  <div class="p-4 space-y-4">
    <div class="flex flex-col items-center gap-3 rounded-lg border border-dashed py-8 px-4 text-center">
      <div class="rounded-full bg-muted p-3">
        <Unplug class="h-5 w-5 text-muted-foreground" />
      </div>
      <div>
        <p class="text-sm font-medium">Connection required</p>
        <p class="mt-1 text-xs text-muted-foreground leading-relaxed">
          This node needs a connected account to work.
        </p>
        <RouterLink
          :to="{ name: 'connections', params: { workspaceId } }"
          class="mt-2 inline-block text-xs text-primary underline"
        >
          Go to Connections
        </RouterLink>
      </div>
    </div>
  </div>
</template>
