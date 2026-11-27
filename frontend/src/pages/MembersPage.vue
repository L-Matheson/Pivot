<script setup lang="ts">
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import UiAvatar from '@/components/ui/avatar.vue'
import { UserPlus, Users, Shield, MoreHorizontal } from 'lucide-vue-next'

const members: unknown[] = []
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

    <div v-if="members.length === 0" class="py-16 text-center">
      <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
        <Users class="h-6 w-6 text-muted-foreground" />
      </div>
      <h2 class="font-semibold">Just you for now</h2>
      <p class="mt-1 mx-auto max-w-xs text-sm text-muted-foreground">
        Invite team members to collaborate on automations in this workspace.
      </p>
      <UiButton class="mt-5" size="sm">
        <UserPlus class="mr-1 h-4 w-4" />
        Invite member
      </UiButton>
    </div>

    <div v-else>
      <UiCard class="divide-y">
        <div class="flex items-center justify-between p-4 transition-colors hover:bg-accent/30">
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
