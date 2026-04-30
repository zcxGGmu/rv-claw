<template>
  <div class="review-panel">
    <div class="review-panel__header">
      <h3>{{ t('review.title') }}</h3>
      <el-tag :type="verdictType">{{ verdictText }}</el-tag>
    </div>
    
    <div class="review-panel__summary">
      <p>{{ review.summary }}</p>
      <div class="review-panel__meta">
        <span>{{ t('review.iteration', { n: review.iteration }) }}</span>
        <span>{{ t('review.model', { model: review.reviewer_model }) }}</span>
      </div>
    </div>
    
    <div class="review-panel__findings">
      <h4>{{ t('review.findings') }} ({{ review.findings.length }})</h4>
      <div
        v-for="(finding, index) in review.findings"
        :key="index"
        class="review-finding"
        :class="`review-finding--${finding.severity}`"
      >
        <div class="review-finding__header">
          <el-tag :type="severityType(finding.severity)" size="small">
            {{ finding.severity }}
          </el-tag>
          <el-tag type="info" size="small">{{ finding.category }}</el-tag>
          <span class="review-finding__location">
            {{ finding.file }}:{{ finding.line }}
          </span>
        </div>
        <p class="review-finding__description">{{ finding.description }}</p>
        <p v-if="finding.suggestion" class="review-finding__suggestion">
          {{ t('review.suggestion') }}: {{ finding.suggestion }}
        </p>
      </div>
    </div>
    
    <div v-if="review.static_analysis.length > 0" class="review-panel__analysis">
      <h4>{{ t('review.staticAnalysis') }}</h4>
      <el-collapse>
        <el-collapse-item
          v-for="analysis in review.static_analysis"
          :key="analysis.tool"
          :title="`${analysis.tool} (${analysis.findings.length})`"
        >
          <ul>
            <li v-for="(finding, idx) in analysis.findings" :key="idx">
              {{ finding }}
            </li>
          </ul>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReviewVerdict } from '@/contracts/review'

const { t } = useI18n()

interface Props {
  review: ReviewVerdict
}

const props = defineProps<Props>()

const verdictType = computed(() => {
  if (props.review.approved) return 'success'
  return 'danger'
})

const verdictText = computed(() => {
  if (props.review.approved) return t('review.approved')
  return t('review.rejected')
})

const severityType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'major': return 'warning'
    case 'minor': return 'info'
    default: return 'info'
  }
}
</script>

<style scoped>
.review-panel {
  padding: 20px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
}

.review-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.review-panel__header h3 {
  margin: 0;
}

.review-panel__summary {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color);
}

.review-panel__summary p {
  margin: 0 0 8px 0;
  color: var(--el-text-color-regular);
}

.review-panel__meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.review-panel__findings h4 {
  margin: 0 0 12px 0;
}

.review-finding {
  padding: 12px;
  margin-bottom: 12px;
  background-color: white;
  border-radius: 4px;
  border-left: 4px solid var(--el-border-color);
}

.review-finding--critical {
  border-left-color: var(--el-color-danger);
}

.review-finding--major {
  border-left-color: var(--el-color-warning);
}

.review-finding--minor {
  border-left-color: var(--el-color-info);
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
  margin: 0;
  font-size: 12px;
  color: var(--el-color-success);
}

.review-panel__analysis {
  margin-top: 20px;
}

.review-panel__analysis h4 {
  margin: 0 0 12px 0;
}
</style>
