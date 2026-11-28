<script setup lang="ts">
import UiLabel from '@/components/ui/label.vue'

defineProps<{
  config: Record<string, unknown>
  workspaceId: string
  nodeType: string
}>()

const emit = defineEmits<{
  'update-field': [key: string, value: unknown]
}>()
</script>

<template>
  <div class="p-4 space-y-4">
    <div>
      <UiLabel for="transform-type">Operation</UiLabel>
      <select
        id="transform-type"
        :value="(config.operation as string) ?? 'map'"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @change="emit('update-field', 'operation', ($event.target as HTMLSelectElement).value)"
      >
        <option value="map">Map fields</option>
        <option value="filter">Filter rows</option>
        <option value="format">Format output</option>
        <option value="extract">Extract value</option>
      </select>
    </div>
    <div>
      <UiLabel for="expression">Expression</UiLabel>
      <textarea
        id="expression"
        :value="(config.expression as string) ?? ''"
        placeholder="e.g. { name: input.first + ' ' + input.last }"
        rows="3"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @input="emit('update-field', 'expression', ($event.target as HTMLTextAreaElement).value)"
      />
    </div>
  </div>
</template>
