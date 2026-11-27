<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import { ArrowLeft } from 'lucide-vue-next'
import NodeSection from '@/features/workflows/help/NodeSection.vue'
import { triggerNodes } from '@/features/workflows/help/triggerNodes'
import { actionNodes } from '@/features/workflows/help/actionNodes'
import { logicNodes } from '@/features/workflows/help/logicNodes'
import type { NodeDoc, SectionDef } from '@/features/workflows/help/types'
import { sectionHeaderColor } from '@/features/workflows/help/types'

// routing

const router = useRouter()

// data

const sections: SectionDef[] = [
  { id: 'triggers', label: 'Triggers', color: 'emerald', desc: 'Events that start a workflow. Every workflow needs exactly one trigger.' },
  { id: 'actions', label: 'Actions', color: 'blue', desc: 'Operations that do something: send a message, call an API, write data, or reshape output.' },
  { id: 'logic', label: 'Logic', color: 'amber', desc: 'Control flow: branch, loop, or run steps in parallel.' },
]

const allNodes = computed<NodeDoc[]>(() => [...triggerNodes, ...actionNodes, ...logicNodes])

// ui state

const searchQuery = ref('')
const activeSection = ref('triggers')
const expandedNodes = ref<Set<string>>(new Set())


function matchesSearch(node: NodeDoc): boolean {
  if (!searchQuery.value) return true
  const lowerQuery = searchQuery.value.toLowerCase()
  return node.label.toLowerCase().includes(lowerQuery) || node.what.toLowerCase().includes(lowerQuery)
}


// computed

// One filtered list per section so the template can show/hide each independently
const filteredTriggers = computed(() => triggerNodes.filter(matchesSearch))
const filteredActions = computed(() => actionNodes.filter(matchesSearch))
const filteredLogic = computed(() => logicNodes.filter(matchesSearch))

// actions

function toggleNode(id: string) {
  if (expandedNodes.value.has(id)) {
    expandedNodes.value.delete(id)
  } else {
    expandedNodes.value.add(id)
  }
}

function expandAll() {
  allNodes.value.forEach((node) => expandedNodes.value.add(node.id))
}

function collapseAll() {
  expandedNodes.value.clear()
}

// scroll tracking

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

    <div class="help-scroll-container flex-1 overflow-y-auto" @scroll="handleScroll">
      <div class="mx-auto max-w-3xl px-6 py-8">
        <NodeSection
          id="triggers"
          title="Triggers"
          :description="sections[0].desc"
          color="emerald"
          :nodes="filteredTriggers"
          :expanded="expandedNodes"
          @toggle="toggleNode"
        />

        <NodeSection
          id="actions"
          title="Actions"
          :description="sections[1].desc"
          color="blue"
          :nodes="filteredActions"
          :expanded="expandedNodes"
          @toggle="toggleNode"
        />

        <NodeSection
          id="logic"
          title="Logic"
          :description="sections[2].desc"
          color="amber"
          :nodes="filteredLogic"
          :expanded="expandedNodes"
          @toggle="toggleNode"
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
