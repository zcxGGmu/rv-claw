<template>
  <div
    class="stage-node"
    :class="{
      'stage-node--active': isActive,
      'stage-node--completed': isCompleted,
      'stage-node--pending': isPending,
      'stage-node--error': hasError,
    }"
    @click="$emit('click', stage)"
  >
    <div class="stage-node__indicator">
      <div class="stage-node__icon">
        <el-icon v-if="isCompleted"><Check /></el-icon>
        <el-icon v-else-if="isActive"><Loading /></el-icon>
        <el-icon v-else-if="hasError"><Close /></el-icon>
        <span v-else class="stage-node__number">{{ index + 1 }}</span>
      </div>
      <div v-if="!isLast" class="stage-node__connector" />
    </div>
    <div class="stage-node__content">
      <div class="stage-node__title">{{ title }}</div>
      <div class="stage-node__description">{{ description }}</div>
      <div v-if="showHumanGate" class="stage-node__badge">
        <el-tag size="small" type="warning">{{ t('pipeline.awaitingReview') }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Loading, Close } from '@element-plus/icons-vue'

const { t } = useI18n()

interface Props {
  stage: string
  title: string
  description: string
  index: number
  currentStage: string
  status: string
  isLast: boolean
  showHumanGate?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'click', stage: string): void
}>()

const stageOrder = ['explore', 'human_gate_explore', 'plan', 'human_gate_plan', 'develop', 'review', 'human_gate_code', 'test', 'human_gate_test']

const currentIndex = computed(() => stageOrder.indexOf(props.currentStage))
const stageIndex = computed(() => stageOrder.indexOf(props.stage))

const isActive = computed(() => props.stage === props.currentStage)
const isCompleted = computed(() => stageIndex.value < currentIndex.value)
const isPending = computed(() => stageIndex.value > currentIndex.value)
const hasError = computed(() => props.status === 'failed' && isActive.value)
</script>

<style scoped>
.stage-node {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.stage-node:hover {
  background-color: var(--el-fill-color-light);
}

.stage-node--active {
  background-color: var(--el-color-primary-light-9);
}

.stage-node__indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stage-node__icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--el-fill-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.stage-node--active .stage-node__icon {
  background-color: var(--el-color-primary);
  color: white;
}

.stage-node--completed .stage-node__icon {
  background-color: var(--el-color-success);
  color: white;
}

.stage-node--error .stage-node__icon {
  background-color: var(--el-color-danger);
  color: white;
}

.stage-node__number {
  font-weight: 600;
}

.stage-node__connector {
  width: 2px;
  height: 40px;
  background-color: var(--el-border-color);
  margin-top: 8px;
}

.stage-node--completed .stage-node__connector {
  background-color: var(--el-color-success);
}

.stage-node__content {
  flex: 1;
  padding-top: 4px;
}

.stage-node__title {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.stage-node__description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.stage-node__badge {
  margin-top: 8px;
}
</style>
