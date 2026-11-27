<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import type { CollapsibleItem } from './collapsible-section.vue'

const colorMap: Record<string, string> = {
  emerald: 'text-emerald-500',
  blue: 'text-blue-500',
  amber: 'text-amber-500',
}

const bgMap: Record<string, string> = {
  emerald: 'bg-emerald-500/10',
  blue: 'bg-blue-500/10',
  amber: 'bg-amber-500/10',
}

const borderMap: Record<string, string> = {
  emerald: 'border-emerald-500/30',
  blue: 'border-blue-500/30',
  amber: 'border-amber-500/30',
}

defineProps<{
  item: CollapsibleItem
  expanded: boolean
}>()

const emit = defineEmits<{
  toggle: [id: string]
}>()
</script>

<template>
  <div :class="['rounded-lg border transition-colors', borderMap[item.color]]">
    <button
      class="flex w-full items-center gap-3 px-4 py-3.5 text-left"
      @click="emit('toggle', item.id)"
    >
      <div :class="[bgMap[item.color], 'rounded-md p-2 shrink-0']">
        <component :is="item.icon" :class="[colorMap[item.color], 'h-4 w-4']" />
      </div>
      <div class="flex-1 min-w-0">
        <span class="text-sm font-medium">{{ item.label }}</span>
        <span class="ml-2 text-sm text-muted-foreground">{{ item.what }}</span>
      </div>
      <ChevronDown
        :class="[
          'h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200',
          expanded ? 'rotate-180' : '',
        ]"
      />
    </button>
    <div v-if="expanded" class="border-t px-4 py-4" :class="borderMap[item.color]">
      <p class="text-xs font-medium text-foreground mb-3">How to use</p>
      <ol class="space-y-2.5 pl-1">
        <li
          v-for="(step, i) in item.how"
          :key="i"
          class="flex gap-3 text-sm text-muted-foreground"
        >
          <span :class="[colorMap[item.color], 'flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold', bgMap[item.color]]">{{ i + 1 }}</span>
          <span class="pt-0.5">{{ step }}</span>
        </li>
      </ol>
    </div>
  </div>
</template>
