<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { Repeat } from 'lucide-vue-next'

defineProps<{
  data: { label: string }
}>()
</script>

<template>
  <div class="rounded-lg border-2 border-amber-500 bg-card px-4 py-3 shadow-sm min-w-[160px]">
    <Handle type="target" :position="Position.Top" class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800" />
    <div class="flex items-center gap-2">
      <div class="rounded-md bg-amber-500/10 p-1.5">
        <Repeat class="h-4 w-4 text-amber-500" />
      </div>
      <div>
        <span class="text-sm font-medium">{{ data.label }}</span>
        <p class="text-[10px] text-muted-foreground leading-tight">Runs for each item</p>
      </div>
    </div>
    <div class="mt-2 flex justify-between px-2 text-[10px] font-medium">
      <span class="text-amber-500">Each</span>
      <span class="text-muted-foreground">Done</span>
    </div>
    <Handle
      id="each"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '25%' }"
      class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
    <Handle
      id="done"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '75%' }"
      class="!bg-muted-foreground !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
  </div>
</template>
