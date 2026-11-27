import { markRaw, type Component } from 'vue'
import type { LucideIcon } from 'lucide-vue-next'
import {
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
  UserCheck,
  Zap,
} from 'lucide-vue-next'

export type NodeCategory = 'trigger' | 'action' | 'logic'

export interface NodeDefinition {
  slug: string
  label: string
  category: NodeCategory
  component: string
  icon: LucideIcon
  description: string
  requiresConnection: boolean
  helpText: string
  helpSteps: string[]
}

export const CATEGORY_COLORS: Record<NodeCategory, string> = {
  trigger: 'emerald',
  action: 'blue',
  logic: 'amber',
}

export const FALLBACK_ICONS: Record<NodeCategory, LucideIcon> = {
  trigger: Zap,
  action: Play,
  logic: GitBranch,
}

const definitions: NodeDefinition[] = [
  // triggers
  {
    slug: 'manual_trigger', label: 'Manual Run', category: 'trigger', component: 'trigger',
    icon: Play, description: 'Start by clicking Run', requiresConnection: false,
    helpText: 'Starts the workflow when you press Run. Useful for testing or one-off tasks.',
    helpSteps: ['Drag onto the canvas.', 'Connect its output to the first action or logic node.', 'Press Run to execute the workflow.'],
  },
  {
    slug: 'email_trigger', label: 'Email Received', category: 'trigger', component: 'trigger',
    icon: Mail, description: 'Fires on matching email', requiresConnection: true,
    helpText: 'Fires when an email matching your filter arrives. Filter by sender, subject, label, or folder.',
    helpSteps: ['Connect an email account on the Connections page.', 'Drag onto the canvas and pick the connected account.', 'Set a filter: label, sender, or subject match.', 'The trigger polls periodically and fires for each new match.'],
  },
  {
    slug: 'webhook_trigger', label: 'Webhook', category: 'trigger', component: 'trigger',
    icon: Webhook, description: 'Fires on incoming POST', requiresConnection: false,
    helpText: 'Fires when an external system sends an HTTP POST to a unique URL generated for this workflow.',
    helpSteps: ['Drag onto the canvas.', 'Copy the generated webhook URL from the node config panel.', 'Paste the URL into the external system.', 'The trigger fires immediately when a POST arrives. The request body becomes the trigger output.'],
  },
  {
    slug: 'schedule_trigger', label: 'Schedule', category: 'trigger', component: 'trigger',
    icon: Clock, description: 'Fires on a cron schedule', requiresConnection: false,
    helpText: 'Fires on a recurring schedule. Use it for periodic reports, syncs, or cleanup tasks.',
    helpSteps: ['Drag onto the canvas.', 'Pick a schedule with the visual picker (e.g. every day at 9 am, every Monday) or write a cron expression.', 'The workflow runs automatically at each scheduled time.'],
  },
  {
    slug: 'database_trigger', label: 'Database Change', category: 'trigger', component: 'trigger',
    icon: Database, description: 'Polls for new rows', requiresConnection: true,
    helpText: 'Polls a connected database for new or changed rows. Fires once per new row detected.',
    helpSteps: ['Connect a database on the Connections page.', 'Drag onto the canvas and select the connection and table.', 'Optionally pick a column to watch for changes.', 'Set the polling interval (e.g. every 5 minutes).'],
  },
  {
    slug: 'api_poll_trigger', label: 'API Poll', category: 'trigger', component: 'trigger',
    icon: Search, description: 'Polls an API endpoint', requiresConnection: false,
    helpText: 'Periodically calls an API endpoint and fires when the response changes or matches a condition.',
    helpSteps: ['Drag onto the canvas.', 'Enter the URL, HTTP method, and optional headers.', 'Set a comparison field and expected value.', 'Set the polling interval. The trigger fires when the condition matches.'],
  },

  // actions
  {
    slug: 'send_email', label: 'Send Email', category: 'action', component: 'action',
    icon: Send, description: 'Send via connected account', requiresConnection: true,
    helpText: 'Sends an email through a connected account. Recipient, subject, and body can use values from earlier steps.',
    helpSteps: ['Connect an email account on the Connections page.', 'Drag onto the canvas and connect it after a trigger or another node.', 'Set the recipient, subject, and body. Use {{step.field}} to insert dynamic values.'],
  },
  {
    slug: 'send_notification', label: 'Send Notification', category: 'action', component: 'action',
    icon: Bell, description: 'Notify user or channel', requiresConnection: false,
    helpText: 'Sends a notification to a user, a Slack channel, or the in-app feed.',
    helpSteps: ['Drag onto the canvas.', 'Choose the target: in-app, Slack channel, or email.', 'Write the message. Use {{step.field}} for dynamic values.'],
  },
  {
    slug: 'write_spreadsheet', label: 'Write to Sheet', category: 'action', component: 'action',
    icon: FileSpreadsheet, description: 'Append row to spreadsheet', requiresConnection: true,
    helpText: 'Appends a row to a connected Google Sheet. Maps values from earlier steps to columns.',
    helpSteps: ['Connect a Google account on the Connections page.', 'Drag onto the canvas and select the spreadsheet and sheet tab.', 'Map each column to a value using {{step.field}} syntax.', 'A new row is appended each time this step runs.'],
  },
  {
    slug: 'http_request', label: 'HTTP Request', category: 'action', component: 'action',
    icon: Globe, description: 'Call any REST endpoint', requiresConnection: false,
    helpText: 'Calls any REST API with a configurable method, headers, and body. The response is available to downstream nodes.',
    helpSteps: ['Drag onto the canvas.', 'Set the URL, method (GET, POST, PUT, DELETE, PATCH), headers, and body.', 'Use {{step.field}} in any field for dynamic values.', 'The response status and body become this node\'s output.'],
  },
  {
    slug: 'transform', label: 'Transform Data', category: 'action', component: 'action',
    icon: Shuffle, description: 'Map, filter, or format', requiresConnection: false,
    helpText: 'Reshapes data between steps: map fields, filter rows, or reformat output.',
    helpSteps: ['Drag onto the canvas between two nodes.', 'Pick the operation: map, filter, or format.', 'Define the mapping or expression.', 'The transformed data is passed to the next node.'],
  },
  {
    slug: 'delay', label: 'Delay', category: 'action', component: 'action',
    icon: Timer, description: 'Wait before continuing', requiresConnection: false,
    helpText: 'Pauses the workflow for a set duration before continuing. Useful for rate limiting or timed sequences.',
    helpSteps: ['Drag onto the canvas.', 'Set the wait duration (seconds, minutes, or hours).', 'The workflow pauses here, then resumes automatically.'],
  },

  // logic
  {
    slug: 'condition', label: 'If / Else', category: 'logic', component: 'condition',
    icon: GitBranch, description: 'Branch on a condition', requiresConnection: false,
    helpText: 'Evaluates a condition and routes the workflow down one of two paths: Yes or No.',
    helpSteps: ['Drag onto the canvas and connect a previous node to the top input.', 'Write a condition using values from earlier steps, e.g. {{email.subject}} contains "urgent".', 'Connect the Yes (green) handle to the true path and the No (red) handle to the false path.', 'Only one path runs per execution.'],
  },
  {
    slug: 'approval', label: 'Approval', category: 'logic', component: 'approval',
    icon: UserCheck, description: 'Require human approval', requiresConnection: false,
    helpText: 'Pauses the workflow until a designated reviewer approves or denies. The workflow branches based on the decision.',
    helpSteps: ['Drag onto the canvas and connect a previous node.', 'Select the reviewer role from workspace roles.', 'Optionally add instructions for the reviewer.', 'The workflow pauses until approved or denied.'],
  },
  {
    slug: 'loop', label: 'Loop', category: 'logic', component: 'loop',
    icon: Repeat, description: 'Iterate over a list', requiresConnection: false,
    helpText: 'Iterates over a list and runs the connected path once per item. After all items, continues down the Done output.',
    helpSteps: ['Drag onto the canvas and connect a node that outputs a list (e.g. database rows).', 'Select the field that contains the list.', 'Connect the Each (amber) handle to the nodes that run for every item.', 'Connect the Done handle to what runs after all items are processed.', 'Inside the loop body, {{loop.item}} refers to the current item.'],
  },
  {
    slug: 'parallel', label: 'Parallel', category: 'logic', component: 'parallel',
    icon: GitFork, description: 'Fan-out to branches', requiresConnection: false,
    helpText: 'Fans out to multiple branches that run at the same time. The workflow continues only after every branch finishes.',
    helpSteps: ['Drag onto the canvas and connect a previous node to the top input.', 'Connect each branch handle to a separate chain of nodes.', 'All branches run concurrently.', 'The workflow continues past the parallel block when every branch completes.'],
  },
]

export const NODE_REGISTRY: ReadonlyArray<NodeDefinition> = definitions

// derived lookups — built once from the single definitions array

export const SLUG_TO_DEFINITION: Record<string, NodeDefinition> = Object.fromEntries(
  definitions.map((d) => [d.slug, d]),
)

export const SLUG_TO_COMPONENT: Record<string, string> = Object.fromEntries(
  definitions.map((d) => [d.slug, d.component]),
)

export const SLUG_TO_LABEL: Record<string, string> = Object.fromEntries(
  definitions.map((d) => [d.slug, d.label]),
)

export const SLUG_TO_ICON: Record<string, LucideIcon> = Object.fromEntries(
  definitions.map((d) => [d.slug, d.icon]),
)

export const LABEL_TO_SLUG: Record<string, string> = Object.fromEntries(
  definitions.map((d) => [d.label, d.slug]),
)

export const REQUIRES_CONNECTION = new Set(
  definitions.filter((d) => d.requiresConnection).map((d) => d.slug),
)

export function nodesByCategory(category: NodeCategory): NodeDefinition[] {
  return definitions.filter((d) => d.category === category)
}

export interface CategorySection {
  id: string
  label: string
  color: string
  description: string
  category: NodeCategory
}

export const CATEGORY_SECTIONS: ReadonlyArray<CategorySection> = [
  { id: 'triggers', label: 'Triggers', color: 'emerald', category: 'trigger', description: 'Events that start a workflow. Every workflow needs exactly one trigger.' },
  { id: 'actions',  label: 'Actions',  color: 'blue',    category: 'action',  description: 'Operations that do something: send a message, call an API, write data, or reshape output.' },
  { id: 'logic',    label: 'Logic',    color: 'amber',   category: 'logic',   description: 'Control flow: branch, loop, or run steps in parallel.' },
]

export interface NodeHelpItem {
  id: string
  label: string
  icon: LucideIcon
  color: 'emerald' | 'blue' | 'amber'
  what: string
  how: string[]
}

export function buildHelpItems(category?: NodeCategory): NodeHelpItem[] {
  const source = category ? nodesByCategory(category) : definitions
  return source.map((d) => ({
    id: d.slug.replace(/_/g, '-'),
    label: d.label,
    icon: d.icon,
    color: CATEGORY_COLORS[d.category] as 'emerald' | 'blue' | 'amber',
    what: d.helpText,
    how: d.helpSteps,
  }))
}

export function buildVueFlowNodeTypes(): Record<string, Component> {
  const components = import.meta.glob<{ default: Component }>(
    './components/*Node.vue',
    { eager: true },
  )

  const map: Record<string, Component> = {}
  for (const [path, mod] of Object.entries(components)) {
    const filename = path.split('/').pop()!.replace('.vue', '')
    const key = filename.replace('Node', '').toLowerCase()
    map[key] = markRaw(mod.default)
  }
  return map
}
