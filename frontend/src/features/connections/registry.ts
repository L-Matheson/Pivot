import type { LucideIcon } from 'lucide-vue-next'
import { Mail, FileSpreadsheet, MessageSquare, Webhook, Globe, Database } from 'lucide-vue-next'

export type ConnectorStatus = 'available' | 'coming_soon'
export type AuthMethod = 'oauth2' | 'api_key' | 'connection_string' | 'none'

export interface ConnectorDefinition {
  slug: string
  name: string
  icon: LucideIcon
  color: string
  bg: string
  authMethod: AuthMethod
  status: ConnectorStatus
}

const definitions: ConnectorDefinition[] = [
  { slug: 'google_gmail',    name: 'Gmail',         icon: Mail,            color: 'text-red-500',     bg: 'bg-red-500/10',     authMethod: 'oauth2',            status: 'available' },
  { slug: 'google_sheets',  name: 'Google Sheets',  icon: FileSpreadsheet, color: 'text-emerald-500', bg: 'bg-emerald-500/10', authMethod: 'oauth2',            status: 'available' },
  { slug: 'slack',          name: 'Slack',          icon: MessageSquare,   color: 'text-purple-500',  bg: 'bg-purple-500/10',  authMethod: 'oauth2',            status: 'coming_soon' },
  { slug: 'webhook',        name: 'Webhook',        icon: Webhook,         color: 'text-orange-500',  bg: 'bg-orange-500/10',  authMethod: 'none',              status: 'available' },
  { slug: 'http_api',       name: 'HTTP API',       icon: Globe,           color: 'text-blue-500',    bg: 'bg-blue-500/10',    authMethod: 'api_key',           status: 'available' },
  { slug: 'postgresql',     name: 'PostgreSQL',     icon: Database,        color: 'text-sky-600',     bg: 'bg-sky-500/10',     authMethod: 'connection_string', status: 'coming_soon' },
]

export const CONNECTOR_REGISTRY: ReadonlyArray<ConnectorDefinition> = definitions

export const SLUG_TO_CONNECTOR: Record<string, ConnectorDefinition> = Object.fromEntries(
  definitions.map((d) => [d.slug, d]),
)

export function connectorsByStatus(status: ConnectorStatus): ConnectorDefinition[] {
  return definitions.filter((d) => d.status === status)
}
