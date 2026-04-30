<template>
  <div class="execution-plan-tree">
    <h3>{{ t('planning.executionPlan') }}</h3>
    <div class="execution-plan-tree__stats">
      <el-statistic :title="t('planning.totalSteps')" :value="plan.dev_steps.length" />
      <el-statistic :title="t('planning.totalTests')" :value="plan.test_cases.length" />
      <el-statistic :title="t('planning.estimatedTokens')" :value="plan.estimated_tokens" />
    </div>
    
    <el-divider />
    
    <div class="execution-plan-tree__steps">
      <h4>{{ t('planning.devSteps') }}</h4>
      <el-steps direction="vertical">
        <el-step
          v-for="step in plan.dev_steps"
          :key="step.id"
          :title="step.description"
          :description="formatStepDescription(step)"
        >
          <template #icon>
            <el-tag :type="riskType(step.risk_level)" size="small">
              {{ step.risk_level }}
            </el-tag>
          </template>
        </el-step>
      </el-steps>
    </div>
    
    <el-divider />
    
    <div class="execution-plan-tree__tests">
      <h4>{{ t('planning.testCases') }}</h4>
      <el-collapse>
        <el-collapse-item
          v-for="test in plan.test_cases"
          :key="test.id"
          :title="test.name"
        >
          <p><strong>{{ t('planning.testType') }}:</strong> {{ test.type }}</p>
          <p><strong>{{ t('planning.testDescription') }}:</strong> {{ test.description }}</p>
          <p><strong>{{ t('planning.expectedResult') }}:</strong> {{ test.expected_result }}</p>
          <el-tag v-if="test.qemu_required" type="warning" size="small">
            {{ t('planning.qemuRequired') }}
          </el-tag>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <div v-if="plan.risk_assessment" class="execution-plan-tree__risk">
      <el-alert
        :title="t('planning.riskAssessment')"
        :description="plan.risk_assessment"
        type="warning"
        show-icon
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionPlan, DevStep } from '@/contracts/planning'

const { t } = useI18n()

interface Props {
  plan: ExecutionPlan
}

defineProps<Props>()

const formatStepDescription = (step: DevStep) => {
  const files = step.target_files.map(f => f.split('/').pop()).join(', ')
  return `${t('planning.files')}: ${files}`
}

const riskType = (risk: string) => {
  switch (risk) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
}
</script>

<style scoped>
.execution-plan-tree {
  padding: 20px;
}

.execution-plan-tree__stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.execution-plan-tree__steps,
.execution-plan-tree__tests {
  margin-bottom: 20px;
}

.execution-plan-tree__steps h4,
.execution-plan-tree__tests h4 {
  margin: 0 0 16px 0;
}

.execution-plan-tree__risk {
  margin-top: 20px;
}
</style>
