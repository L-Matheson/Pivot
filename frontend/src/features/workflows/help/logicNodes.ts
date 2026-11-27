import { GitBranch, Repeat, GitFork } from 'lucide-vue-next'
import type { NodeDoc } from './types'

export const logicNodes: NodeDoc[] = [
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
