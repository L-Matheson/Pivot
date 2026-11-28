<script setup lang="ts">
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'

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
    <div>
      <UiLabel for="channel">Channel or recipient</UiLabel>
      <UiInput
        id="channel"
        :model-value="(config.channel as string) ?? ''"
        placeholder="e.g. #general or user@example.com"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'channel', $event)"
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
        @input="emit('update-field', 'message', ($event.target as HTMLTextAreaElement).value)"
      />
      <p class="mt-1 text-[10px] text-muted-foreground">
        Use <code v-pre class="rounded bg-muted px-1 py-0.5 font-mono">{{field}}</code> to insert values from earlier steps.
      </p>
    </div>
  </div>
</template>
