import type { Component } from 'vue'
import SendEmailConfig from './SendEmailConfig.vue'
import WriteSpreadsheetConfig from './WriteSpreadsheetConfig.vue'
import ApprovalConfig from './ApprovalConfig.vue'
import ManualTriggerConfig from './ManualTriggerConfig.vue'
import WebhookTriggerConfig from './WebhookTriggerConfig.vue'
import ScheduleTriggerConfig from './ScheduleTriggerConfig.vue'
import HttpRequestConfig from './HttpRequestConfig.vue'
import SendNotificationConfig from './SendNotificationConfig.vue'
import TransformConfig from './TransformConfig.vue'
import DelayConfig from './DelayConfig.vue'
import ConditionConfig from './ConditionConfig.vue'
import LoopConfig from './LoopConfig.vue'
import ParallelConfig from './ParallelConfig.vue'
import ConnectionRequiredConfig from './ConnectionRequiredConfig.vue'
import FallbackConfig from './FallbackConfig.vue'

export const nodeConfigComponents: Record<string, Component> = {
  send_email: SendEmailConfig,
  write_spreadsheet: WriteSpreadsheetConfig,
  approval: ApprovalConfig,
  manual_trigger: ManualTriggerConfig,
  webhook_trigger: WebhookTriggerConfig,
  schedule_trigger: ScheduleTriggerConfig,
  http_request: HttpRequestConfig,
  send_notification: SendNotificationConfig,
  transform: TransformConfig,
  delay: DelayConfig,
  condition: ConditionConfig,
  loop: LoopConfig,
  parallel: ParallelConfig,
}

export { ConnectionRequiredConfig, FallbackConfig }
