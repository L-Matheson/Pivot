<script setup lang="ts">
import { computed } from 'vue'
import UiLabel from '@/components/ui/label.vue'
import UiSeparator from '@/components/ui/separator.vue'
import { AlertTriangle } from 'lucide-vue-next'
import { useRoleList } from '@/composables/useRoles'

const props = defineProps<{
  config: Record<string, unknown>
  workspaceId: string
  nodeType: string
}>()

const emit = defineEmits<{
  'update-field': [key: string, value: unknown]
}>()

// data

const workspaceIdRef = computed(() => props.workspaceId)
const { data: roles } = useRoleList(workspaceIdRef)

// computed

const selectableRoles = computed(() =>
  (roles.value ?? []).filter((r) => !r.is_system),
)
</script>

<template>
  <div class="p-4 space-y-4">
    <p class="text-xs text-muted-foreground leading-relaxed">
      Pauses the workflow until a designated reviewer approves or denies. The workflow branches based on the decision.
    </p>

    <div>
      <UiLabel for="approval-role">Reviewer role</UiLabel>
      <select
        id="approval-role"
        :value="(config.required_role_id as string) ?? ''"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @change="emit('update-field', 'required_role_id', ($event.target as HTMLSelectElement).value)"
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
        @input="emit('update-field', 'prompt', ($event.target as HTMLTextAreaElement).value)"
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
</template>
