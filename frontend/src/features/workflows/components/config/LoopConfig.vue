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
      <UiLabel for="list-field">List field</UiLabel>
      <UiInput
        id="list-field"
        :model-value="(config.list_field as string) ?? ''"
        placeholder="e.g. data.items"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'list_field', $event)"
      />
      <p class="mt-1 text-[10px] text-muted-foreground">
        The array from a previous step to iterate over.
      </p>
    </div>
    <div>
      <UiLabel for="item-variable">Item variable name</UiLabel>
      <UiInput
        id="item-variable"
        :model-value="(config.item_variable as string) ?? 'item'"
        placeholder="item"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'item_variable', $event)"
      />
      <p class="mt-1 text-[10px] text-muted-foreground">
        Reference the current item as <code v-pre class="rounded bg-muted px-1 py-0.5 font-mono">{{item}}</code> in downstream nodes.
      </p>
    </div>
    <UiSeparator />
    <div class="grid grid-cols-2 gap-3 text-center text-xs">
      <div class="rounded-md border border-amber-500/20 bg-amber-500/5 p-2">
        <p class="font-medium text-amber-600 dark:text-amber-400">Each</p>
        <p class="text-muted-foreground">Per item</p>
      </div>
      <div class="rounded-md border bg-muted/30 p-2">
        <p class="font-medium">Done</p>
        <p class="text-muted-foreground">After all</p>
      </div>
    </div>
  </div>
</template>
