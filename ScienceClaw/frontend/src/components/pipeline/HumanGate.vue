<template>
  <div class="human-gate">
    <div class="human-gate__header">
      <el-icon size="24" color="var(--el-color-warning)"><Warning /></el-icon>
      <h3>{{ t('pipeline.humanGateTitle') }}</h3>
    </div>
    
    <div class="human-gate__content">
      <p class="human-gate__description">
        {{ t('pipeline.humanGateDescription', { stage: displayStage }) }}
      </p>
      
      <div class="human-gate__artifacts">
        <h4>{{ t('pipeline.reviewArtifacts') }}</h4>
        <el-link 
          v-if="artifactRef" 
          type="primary" 
          @click="$emit('viewArtifact', artifactRef)"
        >
          {{ artifactRef }}
        </el-link>
        <el-empty v-else :description="t('pipeline.noArtifacts')" />
      </div>
    </div>
    
    <div class="human-gate__actions">
      <el-button 
        type="danger" 
        @click="$emit('reject')"
        :disabled="submitting"
      >
        {{ t('pipeline.reject') }}
      </el-button>
      <el-button 
        type="warning" 
        @click="$emit('requestChanges')"
        :disabled="submitting"
      >
        {{ t('pipeline.requestChanges') }}
      </el-button>
      <el-button 
        type="success" 
        @click="$emit('approve')"
        :loading="submitting"
      >
        {{ t('pipeline.approve') }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Warning } from '@element-plus/icons-vue'

const { t } = useI18n()

interface Props {
  stage: string
  artifactRef?: string
  submitting?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'approve'): void
  (e: 'reject'): void
  (e: 'requestChanges'): void
  (e: 'viewArtifact', ref: string): void
}>()

const displayStage = computed(() => {
  const stageMap: Record<string, string> = {
    'human_gate_explore': t('pipeline.stages.explore'),
    'human_gate_plan': t('pipeline.stages.plan'),
    'human_gate_code': t('pipeline.stages.review'),
    'human_gate_test': t('pipeline.stages.test'),
  }
  return stageMap[props.stage] || props.stage
})
</script>

<style scoped>
.human-gate {
  padding: 20px;
  background-color: var(--el-color-warning-light-9);
  border-radius: 8px;
  border: 1px solid var(--el-color-warning-light-5);
}

.human-gate__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.human-gate__header h3 {
  margin: 0;
  color: var(--el-color-warning-dark-2);
}

.human-gate__description {
  color: var(--el-text-color-regular);
  margin-bottom: 16px;
  line-height: 1.6;
}

.human-gate__artifacts {
  margin-bottom: 24px;
  padding: 16px;
  background-color: white;
  border-radius: 4px;
}

.human-gate__artifacts h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.human-gate__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
