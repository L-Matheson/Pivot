<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { getHealth } from './services/api'

const { data, error, isPending } = useQuery({
  queryKey: ['health'],
  queryFn: getHealth,
  retry: false,
})

const status = computed(() => {
  if (isPending.value) return 'loading' as const
  if (error.value || data.value?.status !== 'ok') return 'error' as const
  return 'ok' as const
})
</script>

<template>
  <main>
    <h1>Pivot</h1>
    <p>
      Backend:
      <strong v-if="status === 'loading'">checking…</strong>
      <strong v-else-if="status === 'ok'" class="ok">online</strong>
      <strong v-else class="error">unreachable</strong>
    </p>
    <p v-if="error" class="error">{{ error.message }}</p>
  </main>
</template>

<style scoped>
main {
  font-family: system-ui, sans-serif;
  max-width: 40rem;
  margin: 4rem auto;
  padding: 0 1rem;
}
.ok {
  color: #15803d;
}
.error {
  color: #b91c1c;
}
</style>
