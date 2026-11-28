<script setup lang="ts">
import { computed } from 'vue'
import UiLabel from '@/components/ui/label.vue'
import UiSeparator from '@/components/ui/separator.vue'
import { Plus, Minus } from 'lucide-vue-next'

const props = defineProps<{
  config: Record<string, unknown>
  workspaceId: string
  nodeType: string
}>()

const emit = defineEmits<{
  'update-field': [key: string, value: unknown]
}>()

// computed

const branchCount = computed(() => {
  const count = (props.config.branch_count as number) ?? 2
  return Math.max(2, Math.min(5, count))
})
</script>

<template>
  <div class="p-4 space-y-4">
    <p class="text-xs text-muted-foreground leading-relaxed">
      Fans out to multiple branches that run at the same time. The workflow continues only after every branch finishes.
    </p>
    <div>
      <UiLabel>Branches</UiLabel>
      <div class="mt-1.5 flex items-center gap-3">
        <button
          class="rounded-md border p-1.5 transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-40 disabled:pointer-events-none"
          :disabled="branchCount <= 2"
          @click="emit('update-field', 'branch_count', branchCount - 1)"
        >
          <Minus class="h-3.5 w-3.5" />
        </button>
        <span class="min-w-[3ch] text-center text-sm font-medium tabular-nums">{{ branchCount }}</span>
        <button
          class="rounded-md border p-1.5 transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-40 disabled:pointer-events-none"
          :disabled="branchCount >= 5"
          @click="emit('update-field', 'branch_count', branchCount + 1)"
        >
          <Plus class="h-3.5 w-3.5" />
        </button>
        <span class="text-[10px] text-muted-foreground">2–5</span>
      </div>
    </div>
    <div>
      <UiLabel for="wait-strategy">Wait strategy</UiLabel>
      <select
        id="wait-strategy"
        :value="(config.wait_strategy as string) ?? 'all'"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @change="emit('update-field', 'wait_strategy', ($event.target as HTMLSelectElement).value)"
      >
        <option value="all">Wait for all branches</option>
        <option value="any">Continue after first branch</option>
      </select>
    </div>
    <UiSeparator />
    <div class="flex gap-2 text-center text-xs">
      <div
        v-for="i in branchCount"
        :key="i"
        class="flex-1 rounded-md border border-amber-500/20 bg-amber-500/5 p-2"
      >
        <p class="font-medium text-amber-600 dark:text-amber-400">Branch {{ i }}</p>
      </div>
    </div>
  </div>
</template>
