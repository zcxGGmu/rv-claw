<template>
  <div class="review-finding">
    <div class="review-finding__header">
      <el-tag :type="severityType" size="small">{{ finding.severity }}</el-tag>
      <el-tag type="info" size="small">{{ finding.category }}</el-tag>
      <span class="review-finding__location">{{ finding.file }}:{{ finding.line }}</span>
    </div>
    <p class="review-finding__description">{{ finding.description }}</p>
    <div v-if="finding.suggestion" class="review-finding__suggestion">
      <strong>{{ t('review.suggestion') }}:</strong> {{ finding.suggestion }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReviewFinding as IReviewFinding } from '@/contracts/review'

const { t } = useI18n()

interface Props {
  finding: IReviewFinding
}

const props = defineProps<Props>()

const severityType = computed(() => {
  switch (props.finding.severity) {
    case 'critical': return 'danger'
    case 'major': return 'warning'
    case 'minor': return 'info'
    default: return 'info'
  }
})
</script>

<style scoped>
.review-finding {
  padding: 12px;
  background-color: white;
  border-radius: 4px;
  border-left: 4px solid var(--el-border-color);
  margin-bottom: 8px;
}

.review-finding:deep(.el-tag--danger) + .review-finding {
  border-left-color: var(--el-color-danger);
}

.review-finding__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.review-finding__location {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

.review-finding__description {
  margin: 0 0 8px 0;
  color: var(--el-text-color-regular);
}

.review-finding__suggestion {
  font-size: 12px;
  color: var(--el-color-success);
}
</style>
