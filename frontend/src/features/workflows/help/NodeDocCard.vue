<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import type { NodeDoc } from './types'
import { colorMap, bgMap, sectionBorderColor } from './types'

const props = defineProps<{
  node: NodeDoc
  expanded: boolean
}>()

const emit = defineEmits<{
  toggle: [id: string]
}>()
</script>

<template>
  <div :class="['rounded-lg border transition-colors', sectionBorderColor[node.color]]">
    <button
      class="flex w-full items-center gap-3 px-4 py-3.5 text-left"
      @click="emit('toggle', node.id)"
    >
      <div :class="[bgMap[node.color], 'rounded-md p-2 shrink-0']">
        <component :is="node.icon" :class="[colorMap[node.color], 'h-4 w-4']" />
      </div>
      <div class="flex-1 min-w-0">
        <span class="text-sm font-medium">{{ node.label }}</span>
        <span class="ml-2 text-sm text-muted-foreground">{{ node.what }}</span>
      </div>
      <ChevronDown
        :class="[
          'h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200',
          expanded ? 'rotate-180' : '',
        ]"
      />
    </button>
    <div v-if="expanded" class="border-t px-4 py-4" :class="sectionBorderColor[node.color]">
      <p class="text-xs font-medium text-foreground mb-3">How to use</p>
      <ol class="space-y-2.5 pl-1">
        <li
          v-for="(step, i) in node.how"
          :key="i"
          class="flex gap-3 text-sm text-muted-foreground"
        >
          <span :class="[colorMap[node.color], 'flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold', bgMap[node.color]]">{{ i + 1 }}</span>
          <span class="pt-0.5">{{ step }}</span>
        </li>
      </ol>
    </div>
  </div>
</template>
