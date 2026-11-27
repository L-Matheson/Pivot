<script setup lang="ts">
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import { Plus, Plug, Mail, FileSpreadsheet, MessageSquare, Globe, Database, Webhook } from 'lucide-vue-next'

const connections: unknown[] = []

const integrations = [
  { name: 'Gmail', icon: Mail, color: 'text-red-500', bg: 'bg-red-500/10' },
  { name: 'Google Sheets', icon: FileSpreadsheet, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { name: 'Slack', icon: MessageSquare, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { name: 'Webhook', icon: Webhook, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  { name: 'HTTP API', icon: Globe, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { name: 'PostgreSQL', icon: Database, color: 'text-sky-600', bg: 'bg-sky-500/10' },
]
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

    <div v-if="connections.length === 0" class="py-16 text-center">
      <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
        <Plug class="h-6 w-6 text-muted-foreground" />
      </div>
      <h2 class="font-semibold">No connections yet</h2>
      <p class="mt-1 mx-auto max-w-xs text-sm text-muted-foreground">
        Connect services like Gmail, Google Sheets, and Slack to power your automations.
      </p>
      <UiButton class="mt-5" size="sm">
        <Plus class="mr-1 h-4 w-4" />
        Add connection
      </UiButton>
    </div>

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <!-- Active connection cards -->
    </div>

    <div class="mt-10">
      <h2 class="mb-3 text-sm font-medium text-muted-foreground">Available integrations</h2>
      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="provider in integrations"
          :key="provider.name"
          class="group flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-accent/50"
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
