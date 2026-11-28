<script setup lang="ts">
import UiInput from '@/components/ui/input.vue'
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
      <UiLabel for="delay-amount">Duration</UiLabel>
      <div class="mt-1.5 flex gap-2">
        <UiInput
          id="delay-amount"
          type="number"
          :model-value="String(config.amount ?? 60)"
          class="flex-1"
          @update:model-value="emit('update-field', 'amount', Number($event))"
        />
        <select
          :value="(config.unit as string) ?? 'seconds'"
          class="w-28 rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          @change="emit('update-field', 'unit', ($event.target as HTMLSelectElement).value)"
        >
          <option value="seconds">Seconds</option>
          <option value="minutes">Minutes</option>
          <option value="hours">Hours</option>
        </select>
      </div>
    </div>
    <div class="rounded-md border bg-muted/30 p-3">
      <p class="text-xs text-muted-foreground">
        Pauses the workflow before continuing to the next step. Useful for rate limiting or timed sequences.
      </p>
    </div>
  </div>
</template>
