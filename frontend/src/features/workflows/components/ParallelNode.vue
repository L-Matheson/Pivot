<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { GitFork } from 'lucide-vue-next'

const props = defineProps<{
  data: { label: string; config?: { branch_count?: number } }
  selected?: boolean
}>()

const branchCount = computed(() => {
  const count = props.data.config?.branch_count ?? 2
  return Math.max(2, Math.min(5, count))
})

const branches = computed(() =>
  Array.from({ length: branchCount.value }, (_, i) => ({
    id: `branch-${i + 1}`,
    label: `Branch ${i + 1}`,
    left: `${((i + 1) / (branchCount.value + 1)) * 100}%`,
  })),
)
</script>

<template>
  <div class="rounded-lg border-2 border-amber-500 bg-card px-4 py-3 shadow-sm min-w-[180px]" :class="selected && 'ring-2 ring-amber-500/50 ring-offset-2 ring-offset-background'">
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
      <span v-for="b in branches" :key="b.id">{{ b.label }}</span>
    </div>
    <Handle
      v-for="b in branches"
      :key="b.id"
      :id="b.id"
      type="source"
      :position="Position.Bottom"
      :style="{ left: b.left }"
      class="!bg-amber-500 !h-3 !w-3 !border-2 !border-white dark:!border-neutral-800"
    />
  </div>
</template>
