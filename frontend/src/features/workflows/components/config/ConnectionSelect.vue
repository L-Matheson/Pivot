<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import UiLabel from '@/components/ui/label.vue'
import { useConnectionList } from '@/composables/useConnections'
import { useConnectorRegistry } from '@/composables/useConnectorRegistry'

const props = defineProps<{
  connectionId: string
  workspaceId: string
  nodeType: string
  selectId?: string
}>()

const emit = defineEmits<{
  update: [connectionId: string]
}>()

// data

const workspaceIdRef = computed(() => props.workspaceId)
const { data: allConnections } = useConnectionList(workspaceIdRef)
const { providersForNode } = useConnectorRegistry()

// computed

const matchingConnections = computed(() => {
  const providers = new Set(providersForNode(props.nodeType))
  return (allConnections.value ?? []).filter((c) => providers.has(c.provider))
})
</script>

<template>
  <div>
    <UiLabel :for="selectId ?? 'connection'">Connected account</UiLabel>
    <select
      :id="selectId ?? 'connection'"
      :value="connectionId"
      class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      @change="emit('update', ($event.target as HTMLSelectElement).value)"
    >
      <option value="" disabled>Select a connection...</option>
      <option
        v-for="conn in matchingConnections"
        :key="conn.id"
        :value="conn.id"
      >
        {{ conn.name }}
      </option>
    </select>
    <p v-if="matchingConnections.length === 0" class="mt-1.5 text-xs text-muted-foreground">
      No compatible accounts connected.
      <RouterLink
        :to="{ name: 'connections', params: { workspaceId } }"
        class="text-primary underline"
      >
        Connect one
      </RouterLink>
    </p>
  </div>
</template>
