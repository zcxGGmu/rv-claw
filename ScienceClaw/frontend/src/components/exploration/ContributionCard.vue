<template>
  <div class="contribution-card">
    <div class="contribution-card__header">
      <el-tag :type="typeTag">{{ contribution.contribution_type }}</el-tag>
      <span class="contribution-card__score">
        {{ t('exploration.feasibility') }}: {{ contribution.feasibility_score }}
      </span>
    </div>
    <h4 class="contribution-card__title">{{ contribution.title }}</h4>
    <p class="contribution-card__summary">{{ contribution.summary }}</p>
    <div class="contribution-card__meta">
      <span class="contribution-card__repo">
        <el-icon><Folder /></el-icon>
        {{ contribution.target_repo }}
      </span>
      <span class="contribution-card__complexity">
        {{ t('exploration.complexity') }}: {{ contribution.estimated_complexity }}
      </span>
    </div>
    <div class="contribution-card__files">
      <el-tag
        v-for="file in contribution.target_files.slice(0, 3)"
        :key="file"
        size="small"
        type="info"
      >
        {{ file.split('/').pop() }}
      </el-tag>
      <span v-if="contribution.target_files.length > 3" class="contribution-card__more">
        +{{ contribution.target_files.length - 3 }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Folder } from '@element-plus/icons-vue'
import type { ExplorationResult } from '@/contracts/exploration'

const { t } = useI18n()

interface Props {
  contribution: ExplorationResult
}

const props = defineProps<Props>()

const typeTag = computed(() => {
  switch (props.contribution.contribution_type) {
    case 'isa_extension': return 'success'
    case 'bug_fix': return 'danger'
    case 'cleanup': return 'info'
    default: return ''
  }
})
</script>

<style scoped>
.contribution-card {
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  border: 1px solid var(--el-border-color);
  transition: box-shadow 0.2s;
}

.contribution-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.contribution-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.contribution-card__score {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.contribution-card__title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.contribution-card__summary {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.contribution-card__meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.contribution-card__repo {
  display: flex;
  align-items: center;
  gap: 4px;
}

.contribution-card__files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.contribution-card__more {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
