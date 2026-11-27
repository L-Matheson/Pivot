<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { GitFork } from 'lucide-vue-next'

defineProps<{
  data: { label: string }
}>()
</script>

<template>
  <div class="rounded-lg border-2 border-amber-500 bg-card px-4 py-3 shadow-sm min-w-[180px]">
    <Handle type="target" :position="Position.Top" class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800" />
    <div class="flex items-center gap-2">
      <div class="rounded-md bg-amber-500/10 p-1.5">
        <GitFork class="h-4 w-4 text-amber-500" />
      </div>
      <div>
        <span class="text-sm font-medium">{{ data.label }}</span>
        <p class="text-[10px] text-muted-foreground leading-tight">Fan-out, then merge</p>
      </div>
    </div>
    <div class="mt-2 flex justify-between px-1 text-[10px] font-medium text-amber-500">
      <span>Branch 1</span>
      <span>Branch 2</span>
      <span>Branch 3</span>
    </div>
    <Handle
      id="branch-1"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '20%' }"
      class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
    <Handle
      id="branch-2"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '50%' }"
      class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
    <Handle
      id="branch-3"
      type="source"
      :position="Position.Bottom"
      :style="{ left: '80%' }"
      class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
  </div>
</template>
