<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { SLUG_TO_ICON, FALLBACK_ICONS } from '@/features/workflows/registry'

const props = defineProps<{
  data: { label: string; nodeType?: string }
  selected?: boolean
}>()

const icon = computed(() => {
  if (props.data.nodeType) return SLUG_TO_ICON[props.data.nodeType]
  return FALLBACK_ICONS.action
})
</script>

<template>
  <div class="rounded-lg border-2 border-blue-500 bg-card px-4 py-3 shadow-sm min-w-[160px]" :class="selected && 'ring-2 ring-blue-500/50 ring-offset-2 ring-offset-background'">
    <Handle type="target" :position="Position.Top" class="!bg-blue-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800" />
    <div class="flex items-center gap-2">
      <div class="rounded-md bg-blue-500/10 p-1.5">
        <component :is="icon" class="h-4 w-4 text-blue-500" />
      </div>
      <div>
        <span class="text-sm font-medium">{{ data.label }}</span>
        <p class="text-[10px] text-muted-foreground leading-tight">Action</p>
      </div>
    </div>
    <Handle type="source" :position="Position.Bottom" class="!bg-blue-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800" />
  </div>
</template>
