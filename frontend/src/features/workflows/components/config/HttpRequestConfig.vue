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
      <UiLabel for="method">Method</UiLabel>
      <select
        id="method"
        :value="(config.method as string) ?? 'GET'"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @change="emit('update-field', 'method', ($event.target as HTMLSelectElement).value)"
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
        @update:model-value="emit('update-field', 'url', $event)"
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
        @input="emit('update-field', 'headers', ($event.target as HTMLTextAreaElement).value)"
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
        @input="emit('update-field', 'body', ($event.target as HTMLTextAreaElement).value)"
      />
    </div>
  </div>
</template>
