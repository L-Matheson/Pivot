<script setup lang="ts">
import UiButton from '@/components/ui/button.vue'
import type { Component } from 'vue'

defineProps<{
  icon: Component
  title: string
  description: string
  actionLabel?: string
  actionIcon?: Component
}>()

defineEmits<{
  action: []
}>()
</script>

<template>
  <div class="py-16 text-center">
    <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
      <component :is="icon" class="h-6 w-6 text-muted-foreground" />
    </div>
    <h2 class="font-semibold">{{ title }}</h2>
    <p class="mt-1 mx-auto max-w-xs text-sm text-muted-foreground">
      {{ description }}
    </p>
    <UiButton v-if="actionLabel" class="mt-5" size="sm" @click="$emit('action')">
      <component v-if="actionIcon" :is="actionIcon" class="mr-1 h-4 w-4" />
      {{ actionLabel }}
    </UiButton>
  </div>
</template>
