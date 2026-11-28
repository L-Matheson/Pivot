<script setup lang="ts">
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import ConnectionSelect from './ConnectionSelect.vue'

defineProps<{
  config: Record<string, unknown>
  workspaceId: string
  nodeType: string
}>()

const emit = defineEmits<{
  'update-field': [key: string, value: unknown]
}>()
</script>

<template>
  <div class="p-4 space-y-4">
    <ConnectionSelect
      :connection-id="(config.connection_id as string) ?? ''"
      :workspace-id="workspaceId"
      :node-type="nodeType"
      @update="(id) => emit('update-field', 'connection_id', id)"
    />
    <div>
      <UiLabel for="to">To</UiLabel>
      <UiInput
        id="to"
        :model-value="(config.to as string) ?? ''"
        placeholder="recipient@example.com"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'to', $event)"
      />
    </div>
    <div>
      <UiLabel for="subject">Subject</UiLabel>
      <UiInput
        id="subject"
        :model-value="(config.subject as string) ?? ''"
        placeholder="Email subject"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'subject', $event)"
      />
    </div>
    <div>
      <UiLabel for="email-body">Body</UiLabel>
      <textarea
        id="email-body"
        :value="(config.body as string) ?? ''"
        placeholder="Email body text..."
        rows="4"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @input="emit('update-field', 'body', ($event.target as HTMLTextAreaElement).value)"
      />
    </div>
  </div>
</template>
