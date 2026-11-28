<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import UiSpinner from '@/components/ui/spinner.vue'
import { Plus, Plug, Trash2, FlaskConical, CheckCircle, AlertCircle, Clock } from 'lucide-vue-next'
import { useConnectionList, useDeleteConnection, useTestConnection, useOAuthAuthorize } from '@/composables/useConnections'
import { CONNECTOR_REGISTRY, SLUG_TO_CONNECTOR, connectorsByStatus } from '@/features/connections/registry'
import type { ConnectionListItem } from '@/types/connection'

// routing

const route = useRoute()
const workspaceId = ref(route.params.workspaceId as string)

// data

const { data: connections, isLoading, error } = useConnectionList(workspaceId)
const deleteMutation = useDeleteConnection(workspaceId)
const testMutation = useTestConnection(workspaceId)
const authorizeMutation = useOAuthAuthorize(workspaceId)

// computed

const connectedList = computed(() => connections.value ?? [])
const availableIntegrations = computed(() => connectorsByStatus('available'))
const comingSoonIntegrations = computed(() => connectorsByStatus('coming_soon'))

const connectedProviderSlugs = computed(() =>
  new Set(connectedList.value.map((c: ConnectionListItem) => c.provider)),
)

// ui state

const testResults = ref<Record<string, { ok: boolean; message: string }>>({})
const connectError = ref<string | null>(null)

// actions

async function handleConnect(provider: string) {
  connectError.value = null
  try {
    const { authorize_url } = await authorizeMutation.mutateAsync(provider)
    window.location.href = authorize_url
  } catch (err: unknown) {
    connectError.value = err instanceof Error ? err.message : 'Failed to start authorization.'
  }
}

async function handleDelete(connectionId: string) {
  await deleteMutation.mutateAsync(connectionId)
}

async function handleTest(connectionId: string) {
  try {
    const result = await testMutation.mutateAsync(connectionId)
    testResults.value[connectionId] = { ok: result.ok, message: result.message }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Test failed.'
    testResults.value[connectionId] = { ok: false, message }
  }
}

function statusIcon(status: string) {
  if (status === 'connected') return CheckCircle
  if (status === 'expired') return Clock
  return AlertCircle
}

function statusColor(status: string) {
  if (status === 'connected') return 'text-emerald-500'
  if (status === 'expired') return 'text-amber-500'
  return 'text-destructive'
}
</script>

<template>
  <div class="p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Connections</h1>
    </div>

    <!-- loading -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <UiSpinner class="h-6 w-6" />
    </div>

    <!-- error -->
    <div v-else-if="error" class="text-center text-sm text-destructive py-20">
      Failed to load connections.
    </div>

    <template v-else>
      <!-- connected accounts -->
      <UiEmptyState
        v-if="connectedList.length === 0"
        :icon="Plug"
        title="No connections yet"
        description="Connect services like Gmail and Google Sheets to power your automations."
      />

      <div v-else class="mb-10">
        <h2 class="mb-3 text-sm font-medium text-muted-foreground">Connected accounts</h2>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <UiCard
            v-for="conn in connectedList"
            :key="conn.id"
            class="p-4"
          >
            <div class="flex items-center gap-3">
              <div
                v-if="SLUG_TO_CONNECTOR[conn.provider]"
                :class="['rounded-md p-2', SLUG_TO_CONNECTOR[conn.provider].bg]"
              >
                <component
                  :is="SLUG_TO_CONNECTOR[conn.provider].icon"
                  :class="['h-4 w-4', SLUG_TO_CONNECTOR[conn.provider].color]"
                />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ conn.name }}</p>
                <div class="flex items-center gap-1 mt-0.5">
                  <component :is="statusIcon(conn.status)" :class="['h-3 w-3', statusColor(conn.status)]" />
                  <span :class="['text-xs capitalize', statusColor(conn.status)]">{{ conn.status }}</span>
                </div>
              </div>
              <div class="flex items-center gap-1">
                <UiButton
                  variant="ghost"
                  size="sm"
                  :disabled="testMutation.isPending.value"
                  @click="handleTest(conn.id)"
                >
                  <FlaskConical class="h-3.5 w-3.5" />
                </UiButton>
                <UiButton
                  variant="ghost"
                  size="sm"
                  :disabled="deleteMutation.isPending.value"
                  @click="handleDelete(conn.id)"
                >
                  <Trash2 class="h-3.5 w-3.5 text-destructive" />
                </UiButton>
              </div>
            </div>
            <div
              v-if="testResults[conn.id]"
              :class="[
                'mt-2 rounded px-2 py-1 text-xs',
                testResults[conn.id].ok
                  ? 'bg-emerald-500/10 text-emerald-600'
                  : 'bg-destructive/10 text-destructive',
              ]"
            >
              {{ testResults[conn.id].message }}
            </div>
          </UiCard>
        </div>
      </div>

      <!-- connect error -->
      <div
        v-if="connectError"
        class="mb-4 rounded-md border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
      >
        {{ connectError }}
      </div>

      <!-- available integrations -->
      <div class="mt-10">
        <h2 class="mb-3 text-sm font-medium text-muted-foreground">Available integrations</h2>
        <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="provider in availableIntegrations"
            :key="provider.slug"
            class="group flex items-center gap-3 rounded-lg border p-3 transition-colors hover:border-primary/40"
          >
            <div :class="['rounded-md p-2', provider.bg]">
              <component :is="provider.icon" :class="['h-4 w-4', provider.color]" />
            </div>
            <span class="flex-1 text-sm font-medium">{{ provider.name }}</span>
            <UiButton
              v-if="provider.authMethod === 'oauth2'"
              size="sm"
              :disabled="authorizeMutation.isPending.value"
              @click="handleConnect(provider.slug)"
            >
              {{ connectedProviderSlugs.has(provider.slug) ? 'Add another' : 'Connect' }}
            </UiButton>
            <UiButton v-else variant="outline" size="sm" disabled>
              Connect
            </UiButton>
          </div>
        </div>
      </div>

      <!-- coming soon -->
      <div v-if="comingSoonIntegrations.length > 0" class="mt-8">
        <h2 class="mb-3 text-sm font-medium text-muted-foreground">Coming soon</h2>
        <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="provider in comingSoonIntegrations"
            :key="provider.slug"
            class="flex items-center gap-3 rounded-lg border border-dashed p-3 opacity-50"
          >
            <div :class="['rounded-md p-2', provider.bg]">
              <component :is="provider.icon" :class="['h-4 w-4', provider.color]" />
            </div>
            <span class="flex-1 text-sm font-medium">{{ provider.name }}</span>
            <span class="text-xs text-muted-foreground">Coming soon</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
