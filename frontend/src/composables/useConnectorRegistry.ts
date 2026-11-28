import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { listConnectors } from '@/services/api/connectors'
import type { ConnectorInfo } from '@/types/connection'

export function useConnectorRegistry() {
  const { data: connectors, isLoading } = useQuery({
    queryKey: ['connectors'],
    queryFn: () => listConnectors(),
    staleTime: 5 * 60 * 1000,
  })

  const nodeToProviders = computed<Record<string, string[]>>(() => {
    const map: Record<string, string[]> = {}
    for (const connector of connectors.value ?? []) {
      for (const slug of connector.actions) {
        ;(map[slug] ??= []).push(connector.slug)
      }
      for (const slug of connector.triggers) {
        ;(map[slug] ??= []).push(connector.slug)
      }
    }
    return map
  })

  function providersForNode(nodeSlug: string): string[] {
    return nodeToProviders.value[nodeSlug] ?? []
  }

  function connectorBySlug(slug: string): ConnectorInfo | undefined {
    return (connectors.value ?? []).find((c) => c.slug === slug)
  }

  return {
    connectors,
    isLoading,
    nodeToProviders,
    providersForNode,
    connectorBySlug,
  }
}
