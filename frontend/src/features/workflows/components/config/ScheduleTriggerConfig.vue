<script setup lang="ts">
import UiInput from '@/components/ui/input.vue'
import UiLabel from '@/components/ui/label.vue'
import UiSeparator from '@/components/ui/separator.vue'

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
      <UiLabel for="cron">Cron expression</UiLabel>
      <UiInput
        id="cron"
        :model-value="(config.cron as string) ?? ''"
        placeholder="0 9 * * 1-5"
        class="mt-1.5"
        @update:model-value="emit('update-field', 'cron', $event)"
      />
    </div>
    <div>
      <UiLabel for="timezone">Timezone</UiLabel>
      <select
        id="timezone"
        :value="(config.timezone as string) ?? 'UTC'"
        class="mt-1.5 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        @change="emit('update-field', 'timezone', ($event.target as HTMLSelectElement).value)"
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
          @click="emit('update-field', 'cron', preset.cron)"
        >
          <span class="block font-medium">{{ preset.label }}</span>
          <span class="block text-muted-foreground font-mono">{{ preset.cron }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
