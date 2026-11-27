<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { GitBranch } from 'lucide-vue-next'

defineProps<{
  data: { label: string }
  selected?: boolean
}>()
</script>

<template>
  <div class="rounded-lg border-2 border-amber-500 bg-card px-4 py-3 shadow-sm min-w-[160px]" :class="selected && 'ring-2 ring-amber-500/50 ring-offset-2 ring-offset-background'">
    <Handle type="target" :position="Position.Top" class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800" />
    <div class="flex items-center gap-2">
      <div class="rounded-md bg-amber-500/10 p-1.5">
        <GitBranch class="h-4 w-4 text-amber-500" />
      </div>
      <div>
        <span class="text-sm font-medium">{{ data.label }}</span>
        <p class="text-[10px] text-muted-foreground leading-tight">Branch by condition</p>
      </div>
    </div>
    <div class="mt-2 flex justify-between px-2 text-[10px] font-medium">
      <span class="text-emerald-500">Yes</span>
      <span class="text-red-500">No</span>
    </div>
    <Handle
      id="true"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '25%' }"
      class="!bg-emerald-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
    <Handle
      id="false"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '75%' }"
      class="!bg-red-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
  </div>
</template>
