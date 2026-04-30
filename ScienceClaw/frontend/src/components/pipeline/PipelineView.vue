<template>
  <div class="pipeline-view">
    <div class="pipeline-view__header">
      <h3>{{ t('pipeline.title') }}</h3>
      <div class="pipeline-view__status">
        <el-tag :type="statusType">{{ statusText }}</el-tag>
      </div>
    </div>

    <div class="pipeline-view__stages">
      <StageNode
        v-for="(stage, index) in visibleStages"
        :key="stage.key"
        :stage="stage.key"
        :title="stage.title"
        :description="stage.description"
        :index="index"
        :current-stage="currentStage"
        :status="status"
        :is-last="index === visibleStages.length - 1"
        @click="$emit('selectStage', $event)"
      />
    </div>

    <div v-if="isRunning" class="pipeline-view__progress">
      <el-progress :percentage="progressPercentage" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import StageNode from './StageNode.vue'

const { t } = useI18n()

interface Props {
  currentStage: string
  status: string
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'selectStage', stage: string): void
}>()

const visibleStages = computed(() => [
  { key: 'explore', title: t('pipeline.stages.explore'), description: t('pipeline.stages.exploreDesc') },
  { key: 'plan', title: t('pipeline.stages.plan'), description: t('pipeline.stages.planDesc') },
  { key: 'develop', title: t('pipeline.stages.develop'), description: t('pipeline.stages.developDesc') },
  { key: 'review', title: t('pipeline.stages.review'), description: t('pipeline.stages.reviewDesc') },
  { key: 'test', title: t('pipeline.stages.test'), description: t('pipeline.stages.testDesc') },
])

const isRunning = computed(() => props.status === 'running')

const statusType = computed(() => {
  switch (props.status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'primary'
    default: return 'info'
  }
})

const statusText = computed(() => {
  switch (props.status) {
    case 'completed': return t('pipeline.status.completed')
    case 'failed': return t('pipeline.status.failed')
    case 'running': return t('pipeline.status.running')
    case 'pending': return t('pipeline.status.pending')
    default: return t('pipeline.status.unknown')
  }
})

const progressPercentage = computed(() => {
  const stageOrder = ['explore', 'plan', 'develop', 'review', 'test']
  const cleanStage = props.currentStage.replace('human_gate_', '')
  const currentIndex = stageOrder.indexOf(cleanStage)
  if (currentIndex === -1) return 0
  return Math.round((currentIndex / stageOrder.length) * 100)
})
</script>

<style scoped>
.pipeline-view {
  padding: 16px;
}

.pipeline-view__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.pipeline-view__header h3 {
  margin: 0;
  font-size: 18px;
}

.pipeline-view__stages {
  margin-bottom: 24px;
}

.pipeline-view__progress {
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
}
</style>
