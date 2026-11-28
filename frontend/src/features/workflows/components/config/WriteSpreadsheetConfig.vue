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
      select-id="sheets-connection"
      @update="(id) => emit('update-field', 'connection_id', id)"
    />
    <div>
      <UiLabel for="spreadsheet-id">Spreadsheet ID</UiLabel>
      <UiInput
        id="spreadsheet-id"
        :model-value="(config.spreadsheet_id as string) ?? ''"
        placeholder="e.g. 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'spreadsheet_id', $event)"
      />
      <p class="mt-1 text-[10px] text-muted-foreground">
        The ID from the spreadsheet URL.
      </p>
    </div>
    <div>
      <UiLabel for="sheet-name">Sheet name</UiLabel>
      <UiInput
        id="sheet-name"
        :model-value="(config.sheet_name as string) ?? 'Sheet1'"
        placeholder="Sheet1"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'sheet_name', $event)"
      />
    </div>
    <div>
      <UiLabel for="values">Values <span class="font-normal text-muted-foreground">(JSON array)</span></UiLabel>
      <textarea
        id="values"
        :value="(config.values_json as string) ?? ''"
        placeholder='["Column A", "Column B", "Column C"]'
        rows="3"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @input="emit('update-field', 'values_json', ($event.target as HTMLTextAreaElement).value)"
      />
      <p class="mt-1 text-[10px] text-muted-foreground">
        A flat array becomes one row. A nested array becomes multiple rows.
      </p>
    </div>
  </div>
</template>
