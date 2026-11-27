<script setup lang="ts">
import CollapsibleCard from './collapsible-card.vue'

export interface CollapsibleItem {
  id: string
  label: string
  icon: object
  color: 'emerald' | 'blue' | 'amber'
  what: string
  how: string[]
}

const sectionHeaderColor: Record<string, string> = {
  emerald: 'text-emerald-600 dark:text-emerald-400',
  blue: 'text-blue-600 dark:text-blue-400',
  amber: 'text-amber-600 dark:text-amber-400',
}

defineProps<{
  id: string
  title: string
  description: string
  color: string
  items: CollapsibleItem[]
  expanded: Set<string>
}>()

const emit = defineEmits<{
  toggle: [id: string]
}>()
</script>

<template>
  <section v-if="items.length" :id="id" class="mb-12">
    <div class="mb-5">
      <h2 :class="['text-sm font-semibold mb-1', sectionHeaderColor[color]]">{{ title }}</h2>
      <p class="text-sm text-muted-foreground">{{ description }}</p>
    </div>
    <div class="space-y-2">
      <CollapsibleCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        :expanded="expanded.has(item.id)"
        @toggle="emit('toggle', $event)"
      />
    </div>
  </section>
</template>
