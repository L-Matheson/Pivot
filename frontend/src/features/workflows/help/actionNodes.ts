import { Send, Bell, FileSpreadsheet, Globe, Shuffle, Timer } from 'lucide-vue-next'
import type { NodeDoc } from './types'

export const actionNodes: NodeDoc[] = [
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
