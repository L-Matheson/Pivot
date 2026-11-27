import { Play, Mail, Webhook, Clock, Database, Search } from 'lucide-vue-next'
import type { NodeDoc } from './types'

export const triggerNodes: NodeDoc[] = [
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
