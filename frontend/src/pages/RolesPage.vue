<script setup lang="ts">
import UiButton from '@/components/ui/button.vue'
import UiCard from '@/components/ui/card.vue'
import { Plus, Shield, Lock, MoreHorizontal } from 'lucide-vue-next'

interface RoleStub {
  name: string
  memberCount: number
  isSystem: boolean
  fullAccess: boolean
}

const roles: RoleStub[] = [
  { name: 'Admin', memberCount: 1, isSystem: true, fullAccess: true },
  { name: 'Member', memberCount: 0, isSystem: true, fullAccess: false },
]

const categories = [
  { name: 'Automations', desc: 'view, create, edit, delete' },
  { name: 'Connections', desc: 'view, manage' },
  { name: 'Members', desc: 'view, invite, remove' },
  { name: 'Roles', desc: 'view, manage' },
  { name: 'Settings', desc: 'view, edit' },
  { name: 'Stats', desc: 'view' },
]
</script>

<template>
  <div class="p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Roles</h1>
      <UiButton size="sm">
        <Plus class="mr-1 h-4 w-4" />
        Create role
      </UiButton>
    </div>

    <div class="space-y-2">
      <UiCard
        v-for="role in roles"
        :key="role.name"
        class="flex items-center justify-between p-4"
      >
        <div class="flex items-center gap-3">
          <div class="rounded-md bg-primary/10 p-2">
            <Shield class="h-4 w-4 text-primary" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <p class="text-sm font-medium">{{ role.name }}</p>
              <span
                v-if="role.isSystem"
                class="inline-flex items-center gap-1 rounded-md bg-muted px-1.5 py-0.5 text-xs text-muted-foreground"
              >
                <Lock class="h-3 w-3" />
                System
              </span>
              <span
                v-if="role.fullAccess"
                class="rounded-md bg-emerald-500/10 px-1.5 py-0.5 text-xs font-medium text-emerald-600"
              >
                Full access
              </span>
            </div>
            <p class="text-xs text-muted-foreground">
              {{ role.memberCount }} {{ role.memberCount === 1 ? 'member' : 'members' }}
            </p>
          </div>
        </div>
        <UiButton v-if="!role.isSystem" variant="ghost" size="icon" class="h-8 w-8">
          <MoreHorizontal class="h-4 w-4" />
        </UiButton>
      </UiCard>
    </div>

    <div class="mt-10">
      <h2 class="mb-3 text-sm font-medium text-muted-foreground">Permission categories</h2>
      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="cat in categories"
          :key="cat.name"
          class="rounded-lg border p-3"
        >
          <p class="text-sm font-medium">{{ cat.name }}</p>
          <p class="text-xs text-muted-foreground">{{ cat.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
