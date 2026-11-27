<script setup lang="ts">
import { cn } from '@/lib/utils'
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ name?: string; size?: 'sm' | 'md' | 'lg'; class?: string }>(),
  { size: 'md' },
)

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const sizeClasses = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
}
</script>

<template>
  <div
    :class="
      cn(
        'inline-flex items-center justify-center rounded-full bg-primary font-medium text-primary-foreground',
        sizeClasses[size],
        $props.class,
      )
    "
  >
    {{ initials }}
  </div>
</template>
