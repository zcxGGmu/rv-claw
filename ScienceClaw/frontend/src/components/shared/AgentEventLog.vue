<template>
  <div class="agent-event-log">
    <div class="agent-event-log__header">
      <h4>{{ t('agent.eventLog') }}</h4>
      <el-button size="small" @click="clearEvents">
        {{ t('agent.clear') }}
      </el-button>
    </div>
    <div ref="logContainer" class="agent-event-log__content">
      <div
        v-for="(event, index) in events"
        :key="index"
        class="agent-event"
        :class="`agent-event--${event.type}`"
      >
        <div class="agent-event__time">{{ formatTime(event.timestamp) }}</div>
        <div class="agent-event__icon">
          <el-icon v-if="event.type === 'stage_change'"><RefreshRight /></el-icon>
          <el-icon v-else-if="event.type === 'agent_output'"><ChatDotRound /></el-icon>
          <el-icon v-else-if="event.type === 'review_request'"><Warning /></el-icon>
          <el-icon v-else-if="event.type === 'error'"><CircleClose /></el-icon>
          <el-icon v-else><InfoFilled /></el-icon>
        </div>
        <div class="agent-event__content">
          <div class="agent-event__title">{{ eventTitle(event) }}</div>
          <div v-if="event.message" class="agent-event__message">{{ event.message }}</div>
        </div>
      </div>
      <div v-if="events.length === 0" class="agent-event-log__empty">
        {{ t('agent.noEvents') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RefreshRight, ChatDotRound, Warning, CircleClose, InfoFilled } from '@element-plus/icons-vue'

const { t } = useI18n()

interface AgentEvent {
  type: string
  timestamp: number
  message?: string
  data?: Record<string, any>
}

interface Props {
  events: AgentEvent[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'clear'): void
}>()

const logContainer = ref<HTMLElement>()

const formatTime = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleTimeString()
}

const eventTitle = (event: AgentEvent) => {
  switch (event.type) {
    case 'stage_change': return t('agent.stageChange')
    case 'agent_output': return t('agent.agentOutput')
    case 'review_request': return t('agent.reviewRequest')
    case 'iteration_update': return t('agent.iterationUpdate')
    case 'cost_update': return t('agent.costUpdate')
    case 'error': return t('agent.error')
    case 'completed': return t('agent.completed')
    default: return event.type
  }
}

const clearEvents = () => {
  emit('clear')
}

// Auto-scroll to bottom
watch(() => props.events.length, () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.agent-event-log {
  display: flex;
  flex-direction: column;
  height: 300px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  overflow: hidden;
}

.agent-event-log__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
}

.agent-event-log__header h4 {
  margin: 0;
}

.agent-event-log__content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.agent-event {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  background-color: var(--el-fill-color-light);
}

.agent-event__time {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  min-width: 70px;
}

.agent-event__icon {
  color: var(--el-text-color-secondary);
}

.agent-event__content {
  flex: 1;
}

.agent-event__title {
  font-weight: 500;
  font-size: 13px;
}

.agent-event__message {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.agent-event--error {
  background-color: var(--el-color-danger-light-9);
}

.agent-event--error .agent-event__icon {
  color: var(--el-color-danger);
}

.agent-event-log__empty {
  text-align: center;
  padding: 40px;
  color: var(--el-text-color-secondary);
}
</style>
