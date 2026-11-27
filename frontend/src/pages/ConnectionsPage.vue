<script setup lang="ts">
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import { Plus, Plug } from 'lucide-vue-next'
import type { ConnectionStub } from '@/types/connection'
import { CONNECTOR_REGISTRY } from '@/features/connections/registry'

// data

const connections: ConnectionStub[] = []

// constants — derived from registry

const availableIntegrations = CONNECTOR_REGISTRY
</script>

<template>
  <div class="p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Connections</h1>
      <UiButton size="sm">
        <Plus class="mr-1 h-4 w-4" />
        Add connection
      </UiButton>
    </div>

    <UiEmptyState
      v-if="connections.length === 0"
      :icon="Plug"
      title="No connections yet"
      description="Connect services like Gmail, Google Sheets, and Slack to power your automations."
      action-label="Add connection"
      :action-icon="Plus"
    />

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <!-- Active connection cards -->
    </div>

    <div class="mt-10">
      <h2 class="mb-3 text-sm font-medium text-muted-foreground">Available integrations</h2>
      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="provider in availableIntegrations"
          :key="provider.name"
          class="group flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <div :class="['rounded-md p-2', provider.bg]">
            <component :is="provider.icon" :class="['h-4 w-4', provider.color]" />
          </div>
          <span class="flex-1 text-sm font-medium">{{ provider.name }}</span>
          <UiButton variant="outline" size="sm">Connect</UiButton>
        </div>
      </div>
    </div>
  </div>
</template>
