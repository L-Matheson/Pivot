<script setup lang="ts">
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiAvatar from '@/components/ui/avatar.vue'
import UiEmptyState from '@/components/ui/empty-state.vue'
import { UserPlus, Users, Shield, MoreHorizontal } from 'lucide-vue-next'
import type { MemberStub } from '@/types/member'

// data

const members: MemberStub[] = []
</script>

<template>
  <div class="p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Members</h1>
      <UiButton size="sm">
        <UserPlus class="mr-1 h-4 w-4" />
        Invite member
      </UiButton>
    </div>

    <UiEmptyState
      v-if="members.length === 0"
      :icon="Users"
      title="Just you for now"
      description="Invite team members to collaborate on automations in this workspace."
      action-label="Invite member"
      :action-icon="UserPlus"
    />

    <div v-else>
      <UiCard class="divide-y">
        <div class="flex items-center justify-between p-4 transition-colors hover:bg-muted">
          <div class="flex items-center gap-3">
            <UiAvatar name="Example User" size="sm" />
            <div>
              <p class="text-sm font-medium">Example User</p>
              <p class="text-xs text-muted-foreground">user@example.com</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1 rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
              <Shield class="h-3 w-3" />
              Admin
            </span>
            <UiButton variant="ghost" size="icon" class="h-8 w-8">
              <MoreHorizontal class="h-4 w-4" />
            </UiButton>
          </div>
        </div>
      </UiCard>
    </div>
  </div>
</template>
