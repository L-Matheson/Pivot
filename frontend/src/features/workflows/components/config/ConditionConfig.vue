<script setup lang="ts">
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiSeparator from '@/components/ui/separator.vue'

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
      <UiLabel for="field">Field</UiLabel>
      <UiInput
        id="field"
        :model-value="(config.field as string) ?? ''"
        placeholder="e.g. email.subject"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'field', $event)"
      />
      <p class="mt-1 text-[10px] text-muted-foreground">
        The value from a previous step to evaluate.
      </p>
    </div>
    <div>
      <UiLabel for="operator">Operator</UiLabel>
      <select
        id="operator"
        :value="(config.operator as string) ?? 'equals'"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @change="emit('update-field', 'operator', ($event.target as HTMLSelectElement).value)"
      >
        <option value="equals">Equals</option>
        <option value="not_equals">Not equals</option>
        <option value="contains">Contains</option>
        <option value="not_contains">Does not contain</option>
        <option value="starts_with">Starts with</option>
        <option value="ends_with">Ends with</option>
        <option value="greater_than">Greater than</option>
        <option value="less_than">Less than</option>
        <option value="is_empty">Is empty</option>
        <option value="is_not_empty">Is not empty</option>
      </select>
    </div>
    <div v-if="!['is_empty', 'is_not_empty'].includes((config.operator as string) ?? '')">
      <UiLabel for="value">Value</UiLabel>
      <UiInput
        id="value"
        :model-value="(config.value as string) ?? ''"
        placeholder="Compare to..."
        class="mt-1.5"
        @update:model-value="emit('update-field', 'value', $event)"
      />
    </div>
    <UiSeparator />
    <div class="grid grid-cols-2 gap-3 text-center text-xs">
      <div class="rounded-md border border-emerald-500/20 bg-emerald-500/5 p-2">
        <p class="font-medium text-emerald-600 dark:text-emerald-400">Yes</p>
        <p class="text-muted-foreground">Condition met</p>
      </div>
      <div class="rounded-md border border-red-500/20 bg-red-500/5 p-2">
        <p class="font-medium text-red-600 dark:text-red-400">No</p>
        <p class="text-muted-foreground">Not met</p>
      </div>
    </div>
  </div>
</template>
