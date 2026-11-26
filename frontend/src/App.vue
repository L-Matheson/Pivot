<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getHealth } from './services/api'

const status = ref<'loading' | 'ok' | 'error'>('loading')
const error = ref('')

onMounted(async () => {
  try {
    const health = await getHealth()
    status.value = health.status === 'ok' ? 'ok' : 'error'
  } catch (e) {
    status.value = 'error'
    error.value = e instanceof Error ? e.message : String(e)
  }
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
    <p v-if="error" class="error">{{ error }}</p>
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
