<template>
  <div class="review-history">
    <h3>{{ t('review.history') }}</h3>
    <el-timeline>
      <el-timeline-item
        v-for="record in records"
        :key="record.id"
        :type="recordType(record.decision)"
        :timestamp="formatDate(record.timestamp)"
      >
        <div class="review-history__item">
          <div class="review-history__header">
            <el-tag :type="recordType(record.decision)" size="small">
              {{ record.decision }}
            </el-tag>
            <span class="review-history__reviewer">{{ record.reviewer_id }}</span>
          </div>
          <p v-if="record.notes" class="review-history__notes">{{ record.notes }}</p>
        </div>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ReviewRecord } from '@/types/review'

const { t } = useI18n()

interface Props {
  records: ReviewRecord[]
}

const props = defineProps<Props>()

const recordType = (decision: string) => {
  switch (decision) {
    case 'approve': return 'success'
    case 'reject': return 'danger'
    case 'request_changes': return 'warning'
    default: return 'info'
  }
}

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleString()
}
</script>

<style scoped>
.review-history {
  padding: 20px;
}

.review-history h3 {
  margin: 0 0 20px 0;
}

.review-history__item {
  padding: 8px 0;
}

.review-history__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.review-history__reviewer {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.review-history__notes {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}
</style>
