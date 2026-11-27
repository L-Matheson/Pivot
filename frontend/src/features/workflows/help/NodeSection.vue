<script setup lang="ts">
import type { NodeDoc } from './types'
import { sectionHeaderColor } from './types'
import NodeDocCard from './NodeDocCard.vue'

defineProps<{
  id: string
  title: string
  description: string
  color: string
  nodes: NodeDoc[]
  expanded: Set<string>
}>()

const emit = defineEmits<{
  toggle: [id: string]
}>()
</script>

<template>
  <section v-if="nodes.length" :id="id" class="mb-12">
    <div class="mb-5">
      <h2 :class="['text-sm font-semibold mb-1', sectionHeaderColor[color]]">{{ title }}</h2>
      <p class="text-sm text-muted-foreground">{{ description }}</p>
    </div>
    <div class="space-y-2">
      <NodeDocCard
        v-for="node in nodes"
        :key="node.id"
        :node="node"
        :expanded="expanded.has(node.id)"
        @toggle="emit('toggle', $event)"
      />
    </div>
  </section>
</template>
