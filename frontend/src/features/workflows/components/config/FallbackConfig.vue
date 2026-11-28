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
  <div class="p-4">
    <p class="text-xs text-muted-foreground">
      No configuration options available for this node type.
    </p>
  </div>
</template>
