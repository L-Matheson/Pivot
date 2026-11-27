import type { Component } from 'vue'

export interface NodeDoc {
  id: string
  label: string
  icon: Component
  color: 'emerald' | 'blue' | 'amber'
  what: string
  how: string[]
}

export interface SectionDef {
  id: string
  label: string
  color: 'emerald' | 'blue' | 'amber'
  desc: string
}

export const colorMap: Record<string, string> = {
  emerald: 'text-emerald-500',
  blue: 'text-blue-500',
  amber: 'text-amber-500',
}

export const bgMap: Record<string, string> = {
  emerald: 'bg-emerald-500/10',
  blue: 'bg-blue-500/10',
  amber: 'bg-amber-500/10',
}

export const sectionHeaderColor: Record<string, string> = {
  emerald: 'text-emerald-600 dark:text-emerald-400',
  blue: 'text-blue-600 dark:text-blue-400',
  amber: 'text-amber-600 dark:text-amber-400',
}

export const sectionBorderColor: Record<string, string> = {
  emerald: 'border-emerald-500/30',
  blue: 'border-blue-500/30',
  amber: 'border-amber-500/30',
}
