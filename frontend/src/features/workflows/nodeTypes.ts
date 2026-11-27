export {
  NODE_REGISTRY,
  SLUG_TO_COMPONENT,
  SLUG_TO_LABEL,
  SLUG_TO_ICON,
  LABEL_TO_SLUG,
  REQUIRES_CONNECTION,
  FALLBACK_ICONS,
  CATEGORY_COLORS,
  CATEGORY_SECTIONS,
  nodesByCategory,
  buildVueFlowNodeTypes,
  buildHelpItems,
  type NodeCategory,
  type NodeDefinition,
  type CategorySection,
  type NodeHelpItem,
} from './registry'

export { LABEL_TO_SLUG as NODE_TYPE_SLUGS } from './registry'

export { FALLBACK_ICONS as TRIGGER_FALLBACK_ICON_MAP } from './registry'

import { FALLBACK_ICONS } from './registry'

export const TRIGGER_FALLBACK_ICON = FALLBACK_ICONS.trigger
export const ACTION_FALLBACK_ICON = FALLBACK_ICONS.action
