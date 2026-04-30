<template>
  <div class="test-result-summary">
    <div class="test-result-summary__header">
      <el-result
        :icon="resultIcon"
        :title="resultTitle"
        :sub-title="resultSubtitle"
      />
    </div>
    
    <div class="test-result-summary__stats">
      <el-progress
        :percentage="passRate"
        :color="passRateColor"
        :stroke-width="20"
        striped
      />
      <div class="test-result-summary__numbers">
        <div class="test-stat test-stat--total">
          <span class="test-stat__value">{{ result.total_tests }}</span>
          <span class="test-stat__label">{{ t('testing.total') }}</span>
        </div>
        <div class="test-stat test-stat--passed">
          <span class="test-stat__value">{{ result.passed_tests }}</span>
          <span class="test-stat__label">{{ t('testing.passed') }}</span>
        </div>
        <div class="test-stat test-stat--failed">
          <span class="test-stat__value">{{ result.failed_tests }}</span>
          <span class="test-stat__label">{{ t('testing.failed') }}</span>
        </div>
        <div v-if="result.coverage_percent" class="test-stat test-stat--coverage">
          <span class="test-stat__value">{{ result.coverage_percent.toFixed(1) }}%</span>
          <span class="test-stat__label">{{ t('testing.coverage') }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="result.failure_details.length > 0" class="test-result-summary__failures">
      <h4>{{ t('testing.failures') }}</h4>
      <el-collapse>
        <el-collapse-item
          v-for="(failure, index) in result.failure_details"
          :key="index"
          :title="failure.test_name"
        >
          <el-alert
            :title="failure.error_message"
            type="error"
            :description="failure.stack_trace"
            show-icon
          />
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <div v-if="result.qemu_version" class="test-result-summary__meta">
      <el-descriptions :title="t('testing.environment')" :column="1">
        <el-descriptions-item :label="t('testing.qemuVersion')">
          {{ result.qemu_version }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('testing.logPath')">
          <el-link type="primary">{{ result.test_log_path }}</el-link>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TestResult } from '@/contracts/testing'

const { t } = useI18n()

interface Props {
  result: TestResult
}

const props = defineProps<Props>()

const resultIcon = computed(() => {
  return props.result.passed ? 'success' : 'error'
})

const resultTitle = computed(() => {
  return props.result.passed ? t('testing.allPassed') : t('testing.hasFailures')
})

const resultSubtitle = computed(() => {
  return t('testing.testCount', {
    passed: props.result.passed_tests,
    total: props.result.total_tests,
  })
})

const passRate = computed(() => {
  if (props.result.total_tests === 0) return 0
  return Math.round((props.result.passed_tests / props.result.total_tests) * 100)
})

const passRateColor = computed(() => {
  if (passRate.value >= 90) return '#67C23A'
  if (passRate.value >= 70) return '#E6A23C'
  return '#F56C6C'
})
</script>

<style scoped>
.test-result-summary {
  padding: 20px;
}

.test-result-summary__header {
  margin-bottom: 20px;
}

.test-result-summary__stats {
  margin-bottom: 24px;
}

.test-result-summary__numbers {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.test-stat {
  text-align: center;
}

.test-stat__value {
  display: block;
  font-size: 24px;
  font-weight: 600;
}

.test-stat__label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.test-stat--passed .test-stat__value {
  color: var(--el-color-success);
}

.test-stat--failed .test-stat__value {
  color: var(--el-color-danger);
}

.test-result-summary__failures {
  margin-bottom: 20px;
}

.test-result-summary__failures h4 {
  margin: 0 0 12px 0;
}
</style>
