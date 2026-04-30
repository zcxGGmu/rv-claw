<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCase, getArtifacts, startPipeline as startPipelineApi, subscribeCaseEvents, getHistory, } from '@/api/cases'
import type { Case } from '@/types/case'
import type { Artifact } from '@/types/artifact'
import type { ReviewRecord } from '@/types/review'
import { useI18n } from 'vue-i18n'

// Route & navigation
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Resolve caseId from route params (support multiple patterns)
const caseId = computed<string>(() => {
  const p = route.params as Record<string, any>
  return String(p.caseId ?? p.id ?? '')
})

// State
const caseData = ref<Case | null>(null)
const artifacts = ref<Artifact[]>([])
const history = ref<ReviewRecord[]>([])
const currentStage = ref<string>('explore')
const stageOrder = ['explore', 'plan', 'develop', 'review', 'test']
const isStarting = ref(false)
let unsubscribe: (() => void) | undefined

// Helpers
function stageFromStatus(status: Case['status']): string {
  switch (status) {
    case 'created':
    case 'exploring':
    case 'pending_explore_review':
      return 'explore'
    case 'planning':
    case 'pending_plan_review':
      return 'plan'
    case 'developing':
    case 'pending_code_review':
      return 'develop'
    case 'reviewing':
    case 'pending_test_review':
      return 'review'
    case 'testing':
      return 'test'
    default:
      return 'explore'
  }
}

async function loadCase() {
  if (!caseId.value) return
  try {
    const data = await getCase(caseId.value)
    caseData.value = data
    // derive current stage from status
    currentStage.value = stageFromStatus(data.status)
    await loadArtifactsForStage(currentStage.value)
    history.value = await getHistory(caseId.value)
  } catch (err) {
    console.error('Failed to load case', err)
  }
}

async function loadArtifactsForStage(stage: string) {
  if (!caseId.value) return
  try {
    const list = await getArtifacts(caseId.value, stage)
    artifacts.value = list
  } catch {
    artifacts.value = []
  }
}

async function refreshAll() {
  await loadCase()
}

// Actions
async function startPipeline() {
  if (!caseId.value) return
  isStarting.value = true
  try {
    await startPipelineApi(caseId.value)
    // Refresh to reflect new status
    await refreshAll()
  } catch (err) {
    console.error('Failed to start pipeline', err)
  } finally {
    isStarting.value = false
  }
}

function goBack() {
  // Attempt to go to a known cases list route; fall back to history back
  try {
    router.push('/cases')
  } catch {
    router.back()
  }
}

// SSE subscriptions for real-time events
onMounted(() => {
  if (!caseId.value) return
  loadCase()
  // subscribe to events for this case
  const callbacks = {
    onStageChange: (stage: string, status: string) => {
      currentStage.value = stage
      loadArtifactsForStage(stage)
      // optimistic update of status if we have the object
      if (caseData.value) {
        ;(caseData.value as any).status = status
      }
    },
    onAgentOutput: (_type: string, _content: string) => {
      // could surface live logs; ignored for now
    },
    onReviewRequest: (_stage: string, _artifactRef: string) => {
      // surfaced review request; force refresh to show gating in UI
      refreshAll()
    },
    onIterationUpdate: (_iteration: number) => {
      // no-op for now
    },
    onCostUpdate: (_cost: number) => {
      // could show live cost; ignore here
    },
    onError: (_err: string) => {
      // show error toast if exists
    },
    onCompleted: () => {
      // pipeline finished; refresh
      refreshAll()
    },
  } as any
  unsubscribe = subscribeCaseEvents(caseId.value, callbacks)
})
onUnmounted(() => {
  if (unsubscribe) unsubscribe()
})

// Helpers for UI
const progress = computed(() => {
  const idx = stageOrder.indexOf(currentStage.value)
  return idx >= 0 ? idx : 0
})
const progressPercent = computed(() => Math.min(100, Math.round((progress.value / (stageOrder.length - 1)) * 100)))

function stageState(stage: string) {
  const idx = stageOrder.indexOf(stage)
  if (idx < 0) return 'pending'
  const cur = stageOrder.indexOf(currentStage.value)
  if (idx < cur) return 'completed'
  if (idx === cur) return 'in-progress'
  return 'pending'
}

function formatUSD(value: number) {
  const v = Number(value) || 0
  return `$${v.toFixed(2)}`
}

// Review gating helpers
function needsHumanGate(status?: Case['status'], stage?: string): boolean {
  if (!status || !stage) return false
  const gating: Record<string, string> = {
    explore: 'pending_explore_review',
    plan: 'pending_plan_review',
    develop: 'pending_code_review',
    review: 'pending_test_review',
  }
  return gating[stage] === status
}

function needsReviewGating(status?: Case['status'], stage?: string): boolean {
  // human gate panel is shown when a review is requested for the current stage
  return needsHumanGate(status, stage)
}

// Inline simple actions for human gate (approve/reject) using existing API
import type { ReviewDecision } from '@/types/review'
import { submitReview } from '@/api/cases'

async function approveGate() {
  if (!caseId.value) return
  const decision: ReviewDecision = { action: 'approve' }
  await submitReview(caseId.value, decision)
  await refreshAll()
}

async function rejectGate() {
  if (!caseId.value) return
  const decision: ReviewDecision = { action: 'reject' }
  await submitReview(caseId.value, decision)
  await refreshAll()
}

// Derived data for UI
const needsReview = computed<boolean>(() => needsReviewGating(caseData.value?.status, currentStage.value))
const needsHumanGateFlag = computed<boolean>(() => needsHumanGate(caseData.value?.status, currentStage.value))

// Watch for route id changes to reload data
watch(() => route.params.caseId ?? route.params.id, async () => {
  await loadCase()
})
</script>

<template>
  <div class="case-detail-view" v-if="caseData">
    <!-- Header with basic case info -->
    <div class="case-header" aria-label="Case header">
      <button class="btn-back" @click="goBack">{{ t('case.back_to_list') }}</button>
      <div class="case-title">
        <h2>{{ caseData.title }}</h2>
        <div class="subtle">{{ caseData.id }} • {{ caseData.target_repo }}</div>
      </div>
      <div class="case-status">
        <span class="tag" :class="{ 'completed': caseData?.status === 'completed' }">{{ t(`case.status.${caseData.status}`) || caseData.status }}</span>
      </div>
    </div>

    <!-- Three-column layout -->
    <div class="layout" aria-label="Pipeline layout">
      <!-- Left: Stage navigation -->
      <aside class="left-nav" aria-label="Stage navigation">
        <div class="nav-section">
          <div class="nav-title">{{ t('case.pipeline') }}</div>
          <div v-for="stage in stageOrder" :key="stage" class="stage-item" :class="{'active': currentStage === stage, 'completed': stageState(stage) === 'completed', 'in-progress': stageState(stage) === 'in-progress'}" @click="() => { currentStage = stage; loadArtifactsForStage(stage) }">
            <span class="stage-name">{{ t(`case.stage.${stage}`) }}</span>
            <span class="stage-dot" :class="stageState(stage)"></span>
          </div>
        </div>
        <button class="btn" @click="goBack">{{ t('case.back_to_list') }}</button>
      </aside>

      <!-- Center: Stage content -->
      <section class="center-content" aria-label="Stage content">
        <div class="stage-content" v-if="true">
          <h3 class="stage-heading">{{ t(`case.stage.${currentStage}`) }}</h3>
          <div class="artifact-block" v-if="artifacts.length === 0">
            <em>{{ t('case.no_artifacts') }}</em>
          </div>
          <ul class="artifact-list" v-else>
            <li v-for="a in artifacts" :key="a.id" class="artifact-item">
              <a :href="a.path" target="_blank" rel="noopener">{{ a.filename }}</a>
              <span class="muted">{{ (a.size / 1024).toFixed(1) }} KB • {{ a.content_type }}</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- Right: Review/Human gate panel -->
      <aside class="right-panel" aria-label="Review panel">
        <div v-if="needsHumanGateFlag" class="human-gate-panel">
          <h3>{{ t('case.human_gate.title') }}</h3>
          <p>{{ t('case.human_gate.description') }}</p>
          <div class="gate-actions">
            <button class="btn" @click="approveGate">{{ t('case.human_gate.approve') }}</button>
            <button class="btn secondary" @click="rejectGate">{{ t('case.human_gate.reject') }}</button>
          </div>
        </div>
        <div v-else class="review-panel">
          <h3>{{ t('case.findings') }}</h3>
          <ul class="findings" v-if="history.length > 0">
            <li v-for="h in history" :key="h.id" class="finding-item">
              <span class="badge" :class="'badge-info'">{{ h.stage }}</span>
              <span class="content">{{ h.action }} — {{ h.comment ?? '' }}</span>
              <span class="date">{{ new Date(h.created_at).toLocaleString() }}</span>
            </li>
          </ul>
          <div v-else class="no-findings">{{ t('case.no_findings') }}</div>
        </div>
      </aside>
    </div>

    <!-- Bottom actions -->
    <div class="case-actions" aria-label="Actions">
      <button class="btn primary" @click="startPipeline" :disabled="isStarting || !caseId">
        {{ isStarting ? t('case.starting') : t('case.start_pipeline') }}
      </button>
      <span class="progress-label">{{ t('case.progress') }}: {{ progress + 1 }} / 5</span>
      <div class="lex-spacer" style="flex:1"></div>
      <span class="cost">成本估算: {{ formatUSD(caseData?.cost?.estimated_usd ?? 0) }}</span>
    </div>
  </div>
</template>

<style scoped>
/* Design-system-aligned styles using CSS variables from theme.css */
.case-detail-view {
  padding: 12px 16px;
  color: var(--text-primary);
}
.case-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0 12px 0;
  border-bottom: 1px solid var(--border-light);
}
.btn-back {
  background: var(--Button-secondary-main);
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.case-title {
  text-align: center;
  flex: 1;
}
.case-title h2 { margin: 0; font-size: 1.25rem; }
.case-title .subtle { font-size: 0.85rem; color: var(--text-secondary); }
.case-status .tag {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0,0,0,.04);
}
.layout {
  display: grid;
  grid-template-columns: 260px 1fr 320px;
  gap: 16px;
  align-items: start;
  margin-top: 14px;
}
.left-nav {
  padding: 12px;
  background: var(--background-card);
  border: 1px solid var(--border-light);
  border-radius: 6px;
}
.nav-title { font-weight: 600; margin-bottom: 8px; }
.stage-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 10px; margin-bottom: 6px; border-radius: 6px; cursor: pointer;
}
.stage-item.active { background: var(--fill-tsp-gray-dark); }
.stage-name { font-size: 0.95rem; }
.stage-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.stage-dot.completed { background: var(--function-success); }
.stage-dot.in-progress { background: var(--Button-primary-brand); }
.stage-dot.pending { background: var(--icon-disable); }
.center-content { padding: 0; }
.stage-content { padding: 12px; background: var(--background-card); border: 1px solid var(--border-light); border-radius: 6px; min-height: 360px; }
.stage-heading { margin: 0 0 8px 0; font-size: 1.05rem; }
.artifact-block { color: var(--text-secondary); }
.artifact-list { list-style: none; padding: 0; margin: 0; }
.artifact-item { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border-light); }
.artifact-item a { color: var(--text-brand); text-decoration: none; }
.artifact-item .muted { color: var(--text-secondary); font-size: 0.85rem; }
.right-panel {
  padding: 12px; background: var(--background-card); border: 1px solid var(--border-light); border-radius: 6px; position: sticky; top: 12px; height: fit-content;
}
.human-gate-panel { padding: 8px; }
.gate-actions { display: flex; gap: 8px; margin-top: 8px; }
.review-panel { font-size: 0.95rem; }
.findings { list-style: none; padding: 0; margin: 0; }
.finding-item { display: flex; gap: 8px; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border-light); }
.finding-item .badge { padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.finding-item .date { color: var(--text-secondary); font-size: 11px; margin-left: auto; }
.case-actions { margin-top: 12px; display: flex; align-items: center; gap: 12px; padding-top: 8px; border-top: 1px solid var(--border-light); }
.progress-bar { height: 8px; width: 180px; background: var(--background-gray-main); border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--function-success); width: 0%; }
.btn { background: var(--Button-secondary-main); border: 1px solid var(--border-light); padding: 8px 12px; border-radius: 6px; cursor: pointer; }
.btn.primary { background: var(--Button-primary-brand); color: #fff; border: none; }
.btn.secondary { background: transparent; color: var(--text-primary); border: 1px solid var(--border-light); }
.muted { color: var(--text-secondary); }
.tag { font-family: inherit; }
</style>
