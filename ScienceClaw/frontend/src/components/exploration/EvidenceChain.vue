<template>
  <div class="evidence-chain">
    <h4>{{ t('exploration.evidence') }}</h4>
    <div class="evidence-chain__list">
      <div
        v-for="(evidence, index) in evidences"
        :key="index"
        class="evidence-item"
      >
        <div class="evidence-item__connector" v-if="index > 0" />
        <div class="evidence-item__content">
          <div class="evidence-item__header">
            <el-tag size="small">{{ evidence.source }}</el-tag>
            <el-rate
              v-model="evidence.relevance"
              :max="1"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            />
          </div>
          <p class="evidence-item__text">{{ evidence.content }}</p>
          <el-link
            v-if="evidence.url"
            :href="evidence.url"
            target="_blank"
            type="primary"
            size="small"
          >
            {{ t('exploration.viewSource') }}
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Evidence } from '@/contracts/exploration'

const { t } = useI18n()

interface Props {
  evidences: Evidence[]
}

defineProps<Props>()
</script>

<style scoped>
.evidence-chain {
  padding: 16px;
}

.evidence-chain h4 {
  margin: 0 0 16px 0;
}

.evidence-chain__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.evidence-item {
  display: flex;
  gap: 12px;
}

.evidence-item__connector {
  width: 2px;
  background-color: var(--el-border-color);
  margin-left: 8px;
}

.evidence-item__content {
  flex: 1;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.evidence-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.evidence-item__text {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}
</style>
