<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '@/components/ui/button.vue'
import {
  ArrowLeft,
  Play,
  Mail,
  Webhook,
  Clock,
  Database,
  Search,
  Send,
  Bell,
  FileSpreadsheet,
  Globe,
  Shuffle,
  Timer,
  GitBranch,
  Repeat,
  GitFork,
  ChevronDown,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const workspaceId = route.params.workspaceId as string

const searchQuery = ref('')
const activeSection = ref('triggers')

interface NodeDoc {
  id: string
  label: string
  icon: typeof Play
  color: string
  what: string
  how: string[]
}

const sections = [
  { id: 'triggers', label: 'Triggers', color: 'emerald', desc: 'Events that start a workflow. Every workflow needs exactly one trigger.' },
  { id: 'actions', label: 'Actions', color: 'blue', desc: 'Operations that do something: send a message, call an API, write data, or reshape output.' },
  { id: 'logic', label: 'Logic', color: 'amber', desc: 'Control flow: branch, loop, or run steps in parallel.' },
]

const triggers: NodeDoc[] = [
  {
    id: 'manual-run',
    label: 'Manual Run',
    icon: Play,
    color: 'emerald',
    what: 'Starts the workflow when you press Run. Useful for testing or one-off tasks.',
    how: [
      'Drag onto the canvas.',
      'Connect its output to the first action or logic node.',
      'Press Run to execute the workflow.',
    ],
  },
  {
    id: 'email-received',
    label: 'Email Received',
    icon: Mail,
    color: 'emerald',
    what: 'Fires when an email matching your filter arrives. Filter by sender, subject, label, or folder.',
    how: [
      'Connect an email account on the Connections page.',
      'Drag onto the canvas and pick the connected account.',
      'Set a filter: label, sender, or subject match.',
      'The trigger polls periodically and fires for each new match.',
    ],
  },
  {
    id: 'webhook',
    label: 'Webhook',
    icon: Webhook,
    color: 'emerald',
    what: 'Fires when an external system sends an HTTP POST to a unique URL generated for this workflow.',
    how: [
      'Drag onto the canvas.',
      'Copy the generated webhook URL from the node config panel.',
      'Paste the URL into the external system.',
      'The trigger fires immediately when a POST arrives. The request body becomes the trigger output.',
    ],
  },
  {
    id: 'schedule',
    label: 'Schedule',
    icon: Clock,
    color: 'emerald',
    what: 'Fires on a recurring schedule. Use it for periodic reports, syncs, or cleanup tasks.',
    how: [
      'Drag onto the canvas.',
      'Pick a schedule with the visual picker (e.g. every day at 9 am, every Monday) or write a cron expression.',
      'The workflow runs automatically at each scheduled time.',
    ],
  },
  {
    id: 'database-change',
    label: 'Database Change',
    icon: Database,
    color: 'emerald',
    what: 'Polls a connected database for new or changed rows. Fires once per new row detected.',
    how: [
      'Connect a database on the Connections page.',
      'Drag onto the canvas and select the connection and table.',
      'Optionally pick a column to watch for changes.',
      'Set the polling interval (e.g. every 5 minutes).',
    ],
  },
  {
    id: 'api-poll',
    label: 'API Poll',
    icon: Search,
    color: 'emerald',
    what: 'Periodically calls an API endpoint and fires when the response changes or matches a condition.',
    how: [
      'Drag onto the canvas.',
      'Enter the URL, HTTP method, and optional headers.',
      'Set a comparison field and expected value.',
      'Set the polling interval. The trigger fires when the condition matches.',
    ],
  },
]

const actions: NodeDoc[] = [
  {
    id: 'send-email',
    label: 'Send Email',
    icon: Send,
    color: 'blue',
    what: 'Sends an email through a connected account. Recipient, subject, and body can use values from earlier steps.',
    how: [
      'Connect an email account on the Connections page.',
      'Drag onto the canvas and connect it after a trigger or another node.',
      'Set the recipient, subject, and body. Use {{step.field}} to insert dynamic values.',
    ],
  },
  {
    id: 'send-notification',
    label: 'Send Notification',
    icon: Bell,
    color: 'blue',
    what: 'Sends a notification to a user, a Slack channel, or the in-app feed.',
    how: [
      'Drag onto the canvas.',
      'Choose the target: in-app, Slack channel, or email.',
      'Write the message. Use {{step.field}} for dynamic values.',
    ],
  },
  {
    id: 'write-to-sheet',
    label: 'Write to Sheet',
    icon: FileSpreadsheet,
    color: 'blue',
    what: 'Appends a row to a connected Google Sheet. Maps values from earlier steps to columns.',
    how: [
      'Connect a Google account on the Connections page.',
      'Drag onto the canvas and select the spreadsheet and sheet tab.',
      'Map each column to a value using {{step.field}} syntax.',
      'A new row is appended each time this step runs.',
    ],
  },
  {
    id: 'http-request',
    label: 'HTTP Request',
    icon: Globe,
    color: 'blue',
    what: 'Calls any REST API with a configurable method, headers, and body. The response is available to downstream nodes.',
    how: [
      'Drag onto the canvas.',
      'Set the URL, method (GET, POST, PUT, DELETE, PATCH), headers, and body.',
      'Use {{step.field}} in any field for dynamic values.',
      'The response status and body become this node\'s output.',
    ],
  },
  {
    id: 'transform-data',
    label: 'Transform Data',
    icon: Shuffle,
    color: 'blue',
    what: 'Reshapes data between steps: map fields, filter rows, or reformat output.',
    how: [
      'Drag onto the canvas between two nodes.',
      'Pick the operation: map, filter, or format.',
      'Define the mapping or expression.',
      'The transformed data is passed to the next node.',
    ],
  },
  {
    id: 'delay',
    label: 'Delay',
    icon: Timer,
    color: 'blue',
    what: 'Pauses the workflow for a set duration before continuing. Useful for rate limiting or timed sequences.',
    how: [
      'Drag onto the canvas.',
      'Set the wait duration (seconds, minutes, or hours).',
      'The workflow pauses here, then resumes automatically.',
    ],
  },
]

const logic: NodeDoc[] = [
  {
    id: 'if-else',
    label: 'If / Else',
    icon: GitBranch,
    color: 'amber',
    what: 'Evaluates a condition and routes the workflow down one of two paths: Yes or No.',
    how: [
      'Drag onto the canvas and connect a previous node to the top input.',
      'Write a condition using values from earlier steps, e.g. {{email.subject}} contains "urgent".',
      'Connect the Yes (green) handle to the true path and the No (red) handle to the false path.',
      'Only one path runs per execution.',
    ],
  },
  {
    id: 'loop',
    label: 'Loop',
    icon: Repeat,
    color: 'amber',
    what: 'Iterates over a list and runs the connected path once per item. After all items, continues down the Done output.',
    how: [
      'Drag onto the canvas and connect a node that outputs a list (e.g. database rows).',
      'Select the field that contains the list.',
      'Connect the Each (amber) handle to the nodes that run for every item.',
      'Connect the Done handle to what runs after all items are processed.',
      'Inside the loop body, {{loop.item}} refers to the current item.',
    ],
  },
  {
    id: 'parallel',
    label: 'Parallel',
    icon: GitFork,
    color: 'amber',
    what: 'Fans out to multiple branches that run at the same time. The workflow continues only after every branch finishes.',
    how: [
      'Drag onto the canvas and connect a previous node to the top input.',
      'Connect each branch handle to a separate chain of nodes.',
      'All branches run concurrently.',
      'The workflow continues past the parallel block when every branch completes.',
    ],
  },
]

const allNodes = computed(() => [...triggers, ...actions, ...logic])

const filteredTriggers = computed(() =>
  triggers.filter((n) => matchSearch(n)),
)
const filteredActions = computed(() =>
  actions.filter((n) => matchSearch(n)),
)
const filteredLogic = computed(() =>
  logic.filter((n) => matchSearch(n)),
)

function matchSearch(node: NodeDoc): boolean {
  if (!searchQuery.value) return true
  const q = searchQuery.value.toLowerCase()
  return (
    node.label.toLowerCase().includes(q) ||
    node.what.toLowerCase().includes(q)
  )
}

const expanded = ref<Set<string>>(new Set())

function toggle(id: string) {
  if (expanded.value.has(id)) {
    expanded.value.delete(id)
  } else {
    expanded.value.add(id)
  }
}

function isExpanded(id: string) {
  return expanded.value.has(id)
}

function expandAll() {
  allNodes.value.forEach((n) => expanded.value.add(n.id))
}

function collapseAll() {
  expanded.value.clear()
}

const colorMap: Record<string, string> = {
  emerald: 'text-emerald-500',
  blue: 'text-blue-500',
  amber: 'text-amber-500',
}

const bgMap: Record<string, string> = {
  emerald: 'bg-emerald-500/10',
  blue: 'bg-blue-500/10',
  amber: 'bg-amber-500/10',
}

const sectionHeaderColor: Record<string, string> = {
  emerald: 'text-emerald-600 dark:text-emerald-400',
  blue: 'text-blue-600 dark:text-blue-400',
  amber: 'text-amber-600 dark:text-amber-400',
}

const sectionBorderColor: Record<string, string> = {
  emerald: 'border-emerald-500/30',
  blue: 'border-blue-500/30',
  amber: 'border-amber-500/30',
}

function scrollTo(id: string) {
  activeSection.value = id
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const scrollContainer = ref<HTMLElement | null>(null)

function handleScroll() {
  if (!scrollContainer.value) return
  const scrollTop = scrollContainer.value.scrollTop + 120
  for (const s of sections) {
    const el = document.getElementById(s.id)
    if (el && el.offsetTop <= scrollTop) {
      activeSection.value = s.id
    }
  }
}

onMounted(() => {
  nextTick(() => {
    scrollContainer.value = document.querySelector('.help-scroll-container')
    scrollContainer.value?.addEventListener('scroll', handleScroll)
  })
})

onUnmounted(() => {
  scrollContainer.value?.removeEventListener('scroll', handleScroll)
})

function goBack() {
  router.back()
}
</script>

<template>
  <div class="flex h-full flex-col overflow-hidden">
    <!-- Header -->
    <header class="shrink-0 border-b bg-background px-6 py-5">
      <div class="mx-auto max-w-3xl">
        <div class="flex items-center gap-3 mb-4">
          <UiButton variant="ghost" size="icon" @click="goBack">
            <ArrowLeft class="h-4 w-4" />
          </UiButton>
          <div>
            <h1 class="text-lg font-semibold tracking-tight">Workflow nodes</h1>
            <p class="text-sm text-muted-foreground">
              What each node does and how to wire it up
            </p>
          </div>
        </div>

        <!-- Search + jump nav -->
        <div class="flex items-center gap-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search nodes..."
            class="h-9 w-full max-w-xs rounded-md border bg-background px-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <nav class="flex items-center gap-1">
            <button
              v-for="s in sections"
              :key="s.id"
              :class="[
                'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                activeSection === s.id
                  ? sectionHeaderColor[s.color] + ' bg-muted'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50',
              ]"
              @click="scrollTo(s.id)"
            >
              {{ s.label }}
            </button>
          </nav>
          <div class="ml-auto flex gap-1 text-xs text-muted-foreground">
            <button class="rounded px-2 py-1 hover:bg-muted transition-colors" @click="expandAll">Expand all</button>
            <button class="rounded px-2 py-1 hover:bg-muted transition-colors" @click="collapseAll">Collapse all</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Content -->
    <div class="help-scroll-container flex-1 overflow-y-auto">
      <div class="mx-auto max-w-3xl px-6 py-8">

        <!-- Triggers -->
        <section v-if="filteredTriggers.length" id="triggers" class="mb-12">
          <div class="mb-5">
            <h2 :class="['text-sm font-semibold mb-1', sectionHeaderColor['emerald']]">Triggers</h2>
            <p class="text-sm text-muted-foreground">{{ sections[0].desc }}</p>
          </div>
          <div class="space-y-2">
            <div
              v-for="node in filteredTriggers"
              :key="node.id"
              :class="['rounded-lg border transition-colors', sectionBorderColor[node.color]]"
            >
              <button
                class="flex w-full items-center gap-3 px-4 py-3.5 text-left"
                @click="toggle(node.id)"
              >
                <div :class="[bgMap[node.color], 'rounded-md p-2 shrink-0']">
                  <component :is="node.icon" :class="[colorMap[node.color], 'h-4 w-4']" />
                </div>
                <div class="flex-1 min-w-0">
                  <span class="text-sm font-medium">{{ node.label }}</span>
                  <span class="ml-2 text-sm text-muted-foreground">{{ node.what }}</span>
                </div>
                <ChevronDown
                  :class="[
                    'h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200',
                    isExpanded(node.id) ? 'rotate-180' : '',
                  ]"
                />
              </button>
              <div v-if="isExpanded(node.id)" class="border-t px-4 py-4" :class="sectionBorderColor[node.color]">
                <p class="text-xs font-medium text-foreground mb-3">How to use</p>
                <ol class="space-y-2.5 pl-1">
                  <li
                    v-for="(step, i) in node.how"
                    :key="i"
                    class="flex gap-3 text-sm text-muted-foreground"
                  >
                    <span :class="[colorMap[node.color], 'flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold', bgMap[node.color]]">{{ i + 1 }}</span>
                    <span class="pt-0.5">{{ step }}</span>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </section>

        <!-- Actions -->
        <section v-if="filteredActions.length" id="actions" class="mb-12">
          <div class="mb-5">
            <h2 :class="['text-sm font-semibold mb-1', sectionHeaderColor['blue']]">Actions</h2>
            <p class="text-sm text-muted-foreground">{{ sections[1].desc }}</p>
          </div>
          <div class="space-y-2">
            <div
              v-for="node in filteredActions"
              :key="node.id"
              :class="['rounded-lg border transition-colors', sectionBorderColor[node.color]]"
            >
              <button
                class="flex w-full items-center gap-3 px-4 py-3.5 text-left"
                @click="toggle(node.id)"
              >
                <div :class="[bgMap[node.color], 'rounded-md p-2 shrink-0']">
                  <component :is="node.icon" :class="[colorMap[node.color], 'h-4 w-4']" />
                </div>
                <div class="flex-1 min-w-0">
                  <span class="text-sm font-medium">{{ node.label }}</span>
                  <span class="ml-2 text-sm text-muted-foreground">{{ node.what }}</span>
                </div>
                <ChevronDown
                  :class="[
                    'h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200',
                    isExpanded(node.id) ? 'rotate-180' : '',
                  ]"
                />
              </button>
              <div v-if="isExpanded(node.id)" class="border-t px-4 py-4" :class="sectionBorderColor[node.color]">
                <p class="text-xs font-medium text-foreground mb-3">How to use</p>
                <ol class="space-y-2.5 pl-1">
                  <li
                    v-for="(step, i) in node.how"
                    :key="i"
                    class="flex gap-3 text-sm text-muted-foreground"
                  >
                    <span :class="[colorMap[node.color], 'flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold', bgMap[node.color]]">{{ i + 1 }}</span>
                    <span class="pt-0.5">{{ step }}</span>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </section>

        <!-- Logic -->
        <section v-if="filteredLogic.length" id="logic" class="mb-12">
          <div class="mb-5">
            <h2 :class="['text-sm font-semibold mb-1', sectionHeaderColor['amber']]">Logic</h2>
            <p class="text-sm text-muted-foreground">{{ sections[2].desc }}</p>
          </div>
          <div class="space-y-2">
            <div
              v-for="node in filteredLogic"
              :key="node.id"
              :class="['rounded-lg border transition-colors', sectionBorderColor[node.color]]"
            >
              <button
                class="flex w-full items-center gap-3 px-4 py-3.5 text-left"
                @click="toggle(node.id)"
              >
                <div :class="[bgMap[node.color], 'rounded-md p-2 shrink-0']">
                  <component :is="node.icon" :class="[colorMap[node.color], 'h-4 w-4']" />
                </div>
                <div class="flex-1 min-w-0">
                  <span class="text-sm font-medium">{{ node.label }}</span>
                  <span class="ml-2 text-sm text-muted-foreground">{{ node.what }}</span>
                </div>
                <ChevronDown
                  :class="[
                    'h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200',
                    isExpanded(node.id) ? 'rotate-180' : '',
                  ]"
                />
              </button>
              <div v-if="isExpanded(node.id)" class="border-t px-4 py-4" :class="sectionBorderColor[node.color]">
                <p class="text-xs font-medium text-foreground mb-3">How to use</p>
                <ol class="space-y-2.5 pl-1">
                  <li
                    v-for="(step, i) in node.how"
                    :key="i"
                    class="flex gap-3 text-sm text-muted-foreground"
                  >
                    <span :class="[colorMap[node.color], 'flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold', bgMap[node.color]]">{{ i + 1 }}</span>
                    <span class="pt-0.5">{{ step }}</span>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </section>

        <!-- Empty search -->
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
