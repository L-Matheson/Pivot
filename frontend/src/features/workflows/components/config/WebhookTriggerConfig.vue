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
      Fires when an external system sends an HTTP POST to a unique URL generated for this workflow.
    </p>
    <div class="rounded-md border bg-muted/30 p-3">
      <p class="text-xs text-muted-foreground">
        The webhook URL will be generated when this workflow is activated. Share it with the system that should trigger this workflow.
      </p>
    </div>
  </div>
</template>
