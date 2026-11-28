<script setup lang="ts">
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
    <p class="text-xs text-muted-foreground leading-relaxed">
      Starts the workflow when you press <strong>Run</strong>. No configuration needed.
    </p>
    <div class="rounded-md border bg-muted/30 p-3">
      <p class="text-xs text-muted-foreground">
        Use this for testing or one-off tasks. The workflow will only run when manually triggered.
      </p>
    </div>
  </div>
</template>
