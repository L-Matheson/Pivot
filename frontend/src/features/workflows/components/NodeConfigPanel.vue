<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Node } from '@vue-flow/core'
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiSeparator from '@/components/ui/separator.vue'
import { X, AlertTriangle, Unplug, Zap, Plus, Minus, Trash2 } from 'lucide-vue-next'
import { SLUG_TO_DEFINITION, FALLBACK_ICONS } from '@/features/workflows/registry'
import type { NodeCategory } from '@/features/workflows/registry'
import { useRoleList } from '@/composables/useRoles'

const props = defineProps<{
  node: Node
}>()

const emit = defineEmits<{
  close: []
  updateConfig: [nodeId: string, config: Record<string, unknown>]
  removeNode: [nodeId: string]
}>()

// routing

const route = useRoute()
const workspaceId = computed(() => route.params.workspaceId as string)

// data

const { data: roles } = useRoleList(workspaceId)

// computed

const nodeType = computed(() => (props.node.data?.nodeType as string) ?? props.node.type)
const nodeDef = computed(() => SLUG_TO_DEFINITION[nodeType.value])
const nodeLabel = computed(
  () => (props.node.data?.label as string) ?? nodeDef.value?.label ?? nodeType.value,
)
const config = computed(() => (props.node.data?.config as Record<string, unknown>) ?? {})
const needsConnection = computed(() => nodeDef.value?.requiresConnection ?? false)
const nodeCategory = computed<NodeCategory>(() => nodeDef.value?.category ?? 'action')

const categoryColor = computed(() => {
  const colors: Record<NodeCategory, string> = { trigger: 'emerald', action: 'blue', logic: 'amber' }
  return colors[nodeCategory.value]
})

const nodeIcon = computed(() => nodeDef.value?.icon ?? FALLBACK_ICONS[nodeCategory.value])

const selectableRoles = computed(() =>
  (roles.value ?? []).filter((r) => !r.is_system),
)

const branchCount = computed(() => {
  const count = (config.value.branch_count as number) ?? 2
  return Math.max(2, Math.min(5, count))
})

// actions

function updateField(key: string, value: unknown) {
  emit('updateConfig', props.node.id, { ...config.value, [key]: value })
}
</script>

<template>
  <aside class="flex w-80 flex-col border-l bg-background">
    <!-- header -->
    <div class="flex items-center gap-3 border-b px-4 py-3">
      <div
        class="rounded-md p-1.5"
        :class="{
          'bg-emerald-500/10': categoryColor === 'emerald',
          'bg-blue-500/10': categoryColor === 'blue',
          'bg-amber-500/10': categoryColor === 'amber',
        }"
      >
        <component
          :is="nodeIcon"
          class="h-4 w-4"
          :class="{
            'text-emerald-500': categoryColor === 'emerald',
            'text-blue-500': categoryColor === 'blue',
            'text-amber-500': categoryColor === 'amber',
          }"
        />
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-sm font-medium truncate">{{ nodeLabel }}</h3>
        <p class="text-[10px] text-muted-foreground capitalize">{{ nodeCategory }}</p>
      </div>
      <button
        class="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        @click="emit('close')"
      >
        <X class="h-4 w-4" />
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <!-- connection-dependent: not available yet -->
      <div v-if="needsConnection" class="p-4 space-y-4">
        <div class="flex flex-col items-center gap-3 rounded-lg border border-dashed py-8 px-4 text-center">
          <div class="rounded-full bg-muted p-3">
            <Unplug class="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <p class="text-sm font-medium">Connection required</p>
            <p class="mt-1 text-xs text-muted-foreground leading-relaxed">
              This node needs a connected account to work. Connections will be available in a future update.
            </p>
          </div>
        </div>

        <div class="rounded-md border border-amber-500/20 bg-amber-500/5 p-3">
          <div class="flex items-start gap-2">
            <AlertTriangle class="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
            <p class="text-xs text-muted-foreground">
              You can still place this node in your workflow. It will show an error when you try to run the workflow until a connection is configured.
            </p>
          </div>
        </div>
      </div>

      <!-- approval -->
      <div v-else-if="nodeType === 'approval'" class="p-4 space-y-4">
        <p class="text-xs text-muted-foreground leading-relaxed">
          Pauses the workflow until a designated reviewer approves or denies. The workflow branches based on the decision.
        </p>

        <div>
          <UiLabel for="approval-role">Reviewer role</UiLabel>
          <select
            id="approval-role"
            :value="(config.required_role_id as string) ?? ''"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @change="updateField('required_role_id', ($event.target as HTMLSelectElement).value)"
          >
            <option value="" disabled>Select a role...</option>
            <option
              v-for="role in selectableRoles"
              :key="role.id"
              :value="role.id"
            >
              {{ role.name }}
            </option>
          </select>
          <p class="mt-1 text-[10px] text-muted-foreground">
            Members with this role (or admins) can approve or deny.
          </p>
        </div>

        <div v-if="selectableRoles.length === 0" class="rounded-md border border-amber-500/20 bg-amber-500/5 p-3">
          <div class="flex items-start gap-2">
            <AlertTriangle class="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
            <p class="text-xs text-muted-foreground">
              No custom roles found. Create a custom role in workspace settings to assign reviewers.
            </p>
          </div>
        </div>

        <div>
          <UiLabel for="approval-prompt">Instructions for reviewer</UiLabel>
          <textarea
            id="approval-prompt"
            :value="(config.prompt as string) ?? ''"
            placeholder="Describe what the reviewer should check..."
            rows="3"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @input="updateField('prompt', ($event.target as HTMLTextAreaElement).value)"
          />
        </div>

        <UiSeparator />
        <div class="grid grid-cols-2 gap-3 text-center text-xs">
          <div class="rounded-md border border-emerald-500/20 bg-emerald-500/5 p-2">
            <p class="font-medium text-emerald-600 dark:text-emerald-400">Approved</p>
            <p class="text-muted-foreground">Continue</p>
          </div>
          <div class="rounded-md border border-red-500/20 bg-red-500/5 p-2">
            <p class="font-medium text-red-600 dark:text-red-400">Denied</p>
            <p class="text-muted-foreground">Alternate path</p>
          </div>
        </div>
      </div>

      <!-- manual trigger -->
      <div v-else-if="nodeType === 'manual_trigger'" class="p-4 space-y-4">
        <p class="text-xs text-muted-foreground leading-relaxed">
          Starts the workflow when you press <strong>Run</strong>. No configuration needed.
        </p>
        <div class="rounded-md border bg-muted/30 p-3">
          <p class="text-xs text-muted-foreground">
            Use this for testing or one-off tasks. The workflow will only run when manually triggered.
          </p>
        </div>
      </div>

      <!-- webhook trigger -->
      <div v-else-if="nodeType === 'webhook_trigger'" class="p-4 space-y-4">
        <p class="text-xs text-muted-foreground leading-relaxed">
          Fires when an external system sends an HTTP POST to a unique URL generated for this workflow.
        </p>
        <div class="rounded-md border bg-muted/30 p-3">
          <p class="text-xs text-muted-foreground">
            The webhook URL will be generated when this workflow is activated. Share it with the system that should trigger this workflow.
          </p>
        </div>
      </div>

      <!-- schedule trigger -->
      <div v-else-if="nodeType === 'schedule_trigger'" class="p-4 space-y-4">
        <div>
          <UiLabel for="cron">Cron expression</UiLabel>
          <UiInput
            id="cron"
            :model-value="(config.cron as string) ?? ''"
            placeholder="0 9 * * 1-5"
            class="mt-1.5"
            @update:model-value="updateField('cron', $event)"
          />
        </div>
        <div>
          <UiLabel for="timezone">Timezone</UiLabel>
          <select
            id="timezone"
            :value="(config.timezone as string) ?? 'UTC'"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @change="updateField('timezone', ($event.target as HTMLSelectElement).value)"
          >
            <option value="UTC">UTC</option>
            <option value="America/New_York">Eastern Time</option>
            <option value="America/Chicago">Central Time</option>
            <option value="America/Denver">Mountain Time</option>
            <option value="America/Los_Angeles">Pacific Time</option>
            <option value="Europe/London">London</option>
            <option value="Europe/Berlin">Berlin</option>
            <option value="Asia/Tokyo">Tokyo</option>
          </select>
        </div>
        <UiSeparator />
        <div class="rounded-md border bg-muted/30 p-3 space-y-1.5">
          <p class="text-[11px] font-medium text-muted-foreground">Common patterns</p>
          <div class="grid grid-cols-2 gap-1.5">
            <button
              v-for="preset in [
                { label: 'Every hour', cron: '0 * * * *' },
                { label: 'Daily 9am', cron: '0 9 * * *' },
                { label: 'Weekdays 9am', cron: '0 9 * * 1-5' },
                { label: 'Weekly Mon', cron: '0 9 * * 1' },
              ]"
              :key="preset.cron"
              class="rounded-md border px-2 py-1.5 text-left text-[11px] transition-colors hover:bg-accent hover:text-accent-foreground"
              @click="updateField('cron', preset.cron)"
            >
              <span class="block font-medium">{{ preset.label }}</span>
              <span class="block text-muted-foreground font-mono">{{ preset.cron }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- http request -->
      <div v-else-if="nodeType === 'http_request'" class="p-4 space-y-4">
        <div>
          <UiLabel for="method">Method</UiLabel>
          <select
            id="method"
            :value="(config.method as string) ?? 'GET'"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @change="updateField('method', ($event.target as HTMLSelectElement).value)"
          >
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>PATCH</option>
            <option>DELETE</option>
          </select>
        </div>
        <div>
          <UiLabel for="url">URL</UiLabel>
          <UiInput
            id="url"
            :model-value="(config.url as string) ?? ''"
            placeholder="https://api.example.com/data"
            class="mt-1.5"
            @update:model-value="updateField('url', $event)"
          />
        </div>
        <div>
          <UiLabel for="headers">Headers <span class="font-normal text-muted-foreground">(JSON)</span></UiLabel>
          <textarea
            id="headers"
            :value="(config.headers as string) ?? ''"
            placeholder='{"Content-Type": "application/json"}'
            rows="2"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @input="updateField('headers', ($event.target as HTMLTextAreaElement).value)"
          />
        </div>
        <div>
          <UiLabel for="request-body">Body</UiLabel>
          <textarea
            id="request-body"
            :value="(config.body as string) ?? ''"
            placeholder="Request body (for POST/PUT/PATCH)"
            rows="3"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @input="updateField('body', ($event.target as HTMLTextAreaElement).value)"
          />
        </div>
      </div>

      <!-- send notification -->
      <div v-else-if="nodeType === 'send_notification'" class="p-4 space-y-4">
        <div>
          <UiLabel for="channel">Channel or recipient</UiLabel>
          <UiInput
            id="channel"
            :model-value="(config.channel as string) ?? ''"
            placeholder="e.g. #general or user@example.com"
            class="mt-1.5"
            @update:model-value="updateField('channel', $event)"
          />
        </div>
        <div>
          <UiLabel for="message">Message</UiLabel>
          <textarea
            id="message"
            :value="(config.message as string) ?? ''"
            placeholder="Notification text..."
            rows="3"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @input="updateField('message', ($event.target as HTMLTextAreaElement).value)"
          />
          <p class="mt-1 text-[10px] text-muted-foreground">
            Use <code v-pre class="rounded bg-muted px-1 py-0.5 font-mono">{{field}}</code> to insert values from earlier steps.
          </p>
        </div>
      </div>

      <!-- transform data -->
      <div v-else-if="nodeType === 'transform'" class="p-4 space-y-4">
        <div>
          <UiLabel for="transform-type">Operation</UiLabel>
          <select
            id="transform-type"
            :value="(config.operation as string) ?? 'map'"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @change="updateField('operation', ($event.target as HTMLSelectElement).value)"
          >
            <option value="map">Map fields</option>
            <option value="filter">Filter rows</option>
            <option value="format">Format output</option>
            <option value="extract">Extract value</option>
          </select>
        </div>
        <div>
          <UiLabel for="expression">Expression</UiLabel>
          <textarea
            id="expression"
            :value="(config.expression as string) ?? ''"
            placeholder="e.g. { name: input.first + ' ' + input.last }"
            rows="3"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @input="updateField('expression', ($event.target as HTMLTextAreaElement).value)"
          />
        </div>
      </div>

      <!-- delay -->
      <div v-else-if="nodeType === 'delay'" class="p-4 space-y-4">
        <div>
          <UiLabel for="delay-amount">Duration</UiLabel>
          <div class="mt-1.5 flex gap-2">
            <UiInput
              id="delay-amount"
              type="number"
              :model-value="String(config.amount ?? 60)"
              class="flex-1"
              @update:model-value="updateField('amount', Number($event))"
            />
            <select
              :value="(config.unit as string) ?? 'seconds'"
              class="w-28 rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              @change="updateField('unit', ($event.target as HTMLSelectElement).value)"
            >
              <option value="seconds">Seconds</option>
              <option value="minutes">Minutes</option>
              <option value="hours">Hours</option>
            </select>
          </div>
        </div>
        <div class="rounded-md border bg-muted/30 p-3">
          <p class="text-xs text-muted-foreground">
            Pauses the workflow before continuing to the next step. Useful for rate limiting or timed sequences.
          </p>
        </div>
      </div>

      <!-- condition (if/else) -->
      <div v-else-if="nodeType === 'condition'" class="p-4 space-y-4">
        <div>
          <UiLabel for="field">Field</UiLabel>
          <UiInput
            id="field"
            :model-value="(config.field as string) ?? ''"
            placeholder="e.g. email.subject"
            class="mt-1.5"
            @update:model-value="updateField('field', $event)"
          />
          <p class="mt-1 text-[10px] text-muted-foreground">
            The value from a previous step to evaluate.
          </p>
        </div>
        <div>
          <UiLabel for="operator">Operator</UiLabel>
          <select
            id="operator"
            :value="(config.operator as string) ?? 'equals'"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @change="updateField('operator', ($event.target as HTMLSelectElement).value)"
          >
            <option value="equals">Equals</option>
            <option value="not_equals">Not equals</option>
            <option value="contains">Contains</option>
            <option value="not_contains">Does not contain</option>
            <option value="starts_with">Starts with</option>
            <option value="ends_with">Ends with</option>
            <option value="greater_than">Greater than</option>
            <option value="less_than">Less than</option>
            <option value="is_empty">Is empty</option>
            <option value="is_not_empty">Is not empty</option>
          </select>
        </div>
        <div v-if="!['is_empty', 'is_not_empty'].includes((config.operator as string) ?? '')">
          <UiLabel for="value">Value</UiLabel>
          <UiInput
            id="value"
            :model-value="(config.value as string) ?? ''"
            placeholder="Compare to..."
            class="mt-1.5"
            @update:model-value="updateField('value', $event)"
          />
        </div>
        <UiSeparator />
        <div class="grid grid-cols-2 gap-3 text-center text-xs">
          <div class="rounded-md border border-emerald-500/20 bg-emerald-500/5 p-2">
            <p class="font-medium text-emerald-600 dark:text-emerald-400">Yes</p>
            <p class="text-muted-foreground">Condition met</p>
          </div>
          <div class="rounded-md border border-red-500/20 bg-red-500/5 p-2">
            <p class="font-medium text-red-600 dark:text-red-400">No</p>
            <p class="text-muted-foreground">Not met</p>
          </div>
        </div>
      </div>

      <!-- loop -->
      <div v-else-if="nodeType === 'loop'" class="p-4 space-y-4">
        <div>
          <UiLabel for="list-field">List field</UiLabel>
          <UiInput
            id="list-field"
            :model-value="(config.list_field as string) ?? ''"
            placeholder="e.g. data.items"
            class="mt-1.5"
            @update:model-value="updateField('list_field', $event)"
          />
          <p class="mt-1 text-[10px] text-muted-foreground">
            The array from a previous step to iterate over.
          </p>
        </div>
        <div>
          <UiLabel for="item-variable">Item variable name</UiLabel>
          <UiInput
            id="item-variable"
            :model-value="(config.item_variable as string) ?? 'item'"
            placeholder="item"
            class="mt-1.5"
            @update:model-value="updateField('item_variable', $event)"
          />
          <p class="mt-1 text-[10px] text-muted-foreground">
            Reference the current item as <code v-pre class="rounded bg-muted px-1 py-0.5 font-mono">{{item}}</code> in downstream nodes.
          </p>
        </div>
        <UiSeparator />
        <div class="grid grid-cols-2 gap-3 text-center text-xs">
          <div class="rounded-md border border-amber-500/20 bg-amber-500/5 p-2">
            <p class="font-medium text-amber-600 dark:text-amber-400">Each</p>
            <p class="text-muted-foreground">Per item</p>
          </div>
          <div class="rounded-md border bg-muted/30 p-2">
            <p class="font-medium">Done</p>
            <p class="text-muted-foreground">After all</p>
          </div>
        </div>
      </div>

      <!-- parallel -->
      <div v-else-if="nodeType === 'parallel'" class="p-4 space-y-4">
        <p class="text-xs text-muted-foreground leading-relaxed">
          Fans out to multiple branches that run at the same time. The workflow continues only after every branch finishes.
        </p>
        <div>
          <UiLabel>Branches</UiLabel>
          <div class="mt-1.5 flex items-center gap-3">
            <button
              class="rounded-md border p-1.5 transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-40 disabled:pointer-events-none"
              :disabled="branchCount <= 2"
              @click="updateField('branch_count', branchCount - 1)"
            >
              <Minus class="h-3.5 w-3.5" />
            </button>
            <span class="min-w-[3ch] text-center text-sm font-medium tabular-nums">{{ branchCount }}</span>
            <button
              class="rounded-md border p-1.5 transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-40 disabled:pointer-events-none"
              :disabled="branchCount >= 5"
              @click="updateField('branch_count', branchCount + 1)"
            >
              <Plus class="h-3.5 w-3.5" />
            </button>
            <span class="text-[10px] text-muted-foreground">2–5</span>
          </div>
        </div>
        <div>
          <UiLabel for="wait-strategy">Wait strategy</UiLabel>
          <select
            id="wait-strategy"
            :value="(config.wait_strategy as string) ?? 'all'"
            class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @change="updateField('wait_strategy', ($event.target as HTMLSelectElement).value)"
          >
            <option value="all">Wait for all branches</option>
            <option value="any">Continue after first branch</option>
          </select>
        </div>
        <UiSeparator />
        <div class="flex gap-2 text-center text-xs">
          <div
            v-for="i in branchCount"
            :key="i"
            class="flex-1 rounded-md border border-amber-500/20 bg-amber-500/5 p-2"
          >
            <p class="font-medium text-amber-600 dark:text-amber-400">Branch {{ i }}</p>
          </div>
        </div>
      </div>

      <!-- fallback -->
      <div v-else class="p-4">
        <p class="text-xs text-muted-foreground">
          No configuration options available for this node type.
        </p>
      </div>

      <!-- footer: delete + metadata -->
      <div class="border-t px-4 py-3 space-y-3">
        <button
          class="flex w-full items-center justify-center gap-1.5 rounded-md border border-destructive/30 px-3 py-2 text-xs font-medium text-destructive transition-colors hover:bg-destructive hover:text-destructive-foreground"
          @click="emit('removeNode', node.id)"
        >
          <Trash2 class="h-3.5 w-3.5" />
          Remove node
        </button>
        <p class="text-[10px] text-muted-foreground">
          ID: <code class="rounded bg-muted px-1 py-0.5 font-mono">{{ node.id }}</code>
        </p>
      </div>
    </div>
  </aside>
</template>
