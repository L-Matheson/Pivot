<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import CollapsibleSection from '@/components/ui/collapsible-section.vue'
import type { CollapsibleItem } from '@/components/ui/collapsible-section.vue'
import { ArrowLeft } from 'lucide-vue-next'
import { CATEGORY_SECTIONS, buildHelpItems } from '@/features/workflows/registry'

const sectionHeaderColor: Record<string, string> = {
  emerald: 'text-emerald-600 dark:text-emerald-400',
  blue: 'text-blue-600 dark:text-blue-400',
  amber: 'text-amber-600 dark:text-amber-400',
}

// routing

const router = useRouter()

// data — derived from registry

const sections = CATEGORY_SECTIONS
const triggerItems = buildHelpItems('trigger') as CollapsibleItem[]
const actionItems = buildHelpItems('action') as CollapsibleItem[]
const logicItems = buildHelpItems('logic') as CollapsibleItem[]
const allItems = computed<CollapsibleItem[]>(() => [...triggerItems, ...actionItems, ...logicItems])

// ui state

const searchQuery = ref('')
const activeSection = ref('triggers')
const expandedItems = ref<Set<string>>(new Set())

function matchesSearch(item: CollapsibleItem): boolean {
  if (!searchQuery.value) return true
  const lowerQuery = searchQuery.value.toLowerCase()
  return item.label.toLowerCase().includes(lowerQuery) || item.what.toLowerCase().includes(lowerQuery)
}

// computed — one filtered list per section

const filteredTriggers = computed(() => triggerItems.filter(matchesSearch))
const filteredActions = computed(() => actionItems.filter(matchesSearch))
const filteredLogic = computed(() => logicItems.filter(matchesSearch))

// actions

function toggleItem(id: string) {
  if (expandedItems.value.has(id)) {
    expandedItems.value.delete(id)
  } else {
    expandedItems.value.add(id)
  }
}

function expandAll() {
  allItems.value.forEach((item) => expandedItems.value.add(item.id))
}

function collapseAll() {
  expandedItems.value.clear()
}

function scrollToSection(sectionId: string) {
  activeSection.value = sectionId
  document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function handleScroll(event: Event) {
  const container = event.currentTarget as HTMLElement
  const scrollTop = container.scrollTop + 120
  for (const section of sections) {
    const sectionElement = document.getElementById(section.id)
    if (sectionElement && sectionElement.offsetTop <= scrollTop) {
      activeSection.value = section.id
    }
  }
}
</script>

<template>
  <div class="flex h-full flex-col overflow-hidden">
    <header class="shrink-0 border-b bg-background px-6 py-5">
      <div class="mx-auto max-w-3xl">
        <div class="flex items-center gap-3 mb-4">
          <UiButton variant="ghost" size="icon" @click="router.back()">
            <ArrowLeft class="h-4 w-4" />
          </UiButton>
          <div>
            <h1 class="text-lg font-semibold tracking-tight">Workflow nodes</h1>
            <p class="text-sm text-muted-foreground">
              What each node does and how to wire it up
            </p>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search nodes..."
            class="h-9 w-full max-w-xs rounded-md border bg-background px-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <nav class="flex items-center gap-1">
            <button
              v-for="section in sections"
              :key="section.id"
              :class="[
                'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                activeSection === section.id
                  ? sectionHeaderColor[section.color] + ' bg-muted'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50',
              ]"
              @click="scrollToSection(section.id)"
            >
              {{ section.label }}
            </button>
          </nav>
          <div class="ml-auto flex gap-1 text-xs text-muted-foreground">
            <button class="rounded px-2 py-1 hover:bg-muted transition-colors" @click="expandAll">Expand all</button>
            <button class="rounded px-2 py-1 hover:bg-muted transition-colors" @click="collapseAll">Collapse all</button>
          </div>
        </div>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto" @scroll="handleScroll">
      <div class="mx-auto max-w-3xl px-6 py-8">
        <CollapsibleSection
          id="triggers"
          title="Triggers"
          :description="sections[0].description"
          color="emerald"
          :items="filteredTriggers"
          :expanded="expandedItems"
          @toggle="toggleItem"
        />

        <CollapsibleSection
          id="actions"
          title="Actions"
          :description="sections[1].description"
          color="blue"
          :items="filteredActions"
          :expanded="expandedItems"
          @toggle="toggleItem"
        />

        <CollapsibleSection
          id="logic"
          title="Logic"
          :description="sections[2].description"
          color="amber"
          :items="filteredLogic"
          :expanded="expandedItems"
          @toggle="toggleItem"
        />

        <div
          v-if="!filteredTriggers.length && !filteredActions.length && !filteredLogic.length"
          class="py-16 text-center"
        >
          <p class="text-sm text-muted-foreground">No nodes match "{{ searchQuery }}"</p>
          <button class="mt-2 text-sm text-primary hover:underline" @click="searchQuery = ''">Clear search</button>
        </div>
      </div>
    </div>
  </div>
</template>
