import { ref, computed } from 'vue'
import type { PipelineStage } from '@/types/pipeline'

export interface PipelineState {
  caseId: string
  currentStage: string
  stages: PipelineStage[]
  isRunning: boolean
  status: 'pending' | 'running' | 'completed' | 'failed'
}

export function usePipelineStore() {
  const state = ref<PipelineState>({
    caseId: '',
    currentStage: 'explore',
    stages: [],
    isRunning: false,
    status: 'pending',
  })

  const isAtHumanGate = computed(() => {
    return state.value.currentStage.startsWith('human_gate_')
  })

  const currentStageDisplay = computed(() => {
    return state.value.currentStage.replace('human_gate_', '')
  })

  const progress = computed(() => {
    const stageOrder = ['explore', 'plan', 'develop', 'review', 'test']
    const current = state.value.currentStage.replace('human_gate_', '')
    const index = stageOrder.indexOf(current)
    if (index === -1) return 0
    return Math.round((index / stageOrder.length) * 100)
  })

  const setCaseId = (caseId: string) => {
    state.value.caseId = caseId
  }

  const setStage = (stage: string) => {
    state.value.currentStage = stage
  }

  const setStatus = (status: PipelineState['status']) => {
    state.value.status = status
    state.value.isRunning = status === 'running'
  }

  const reset = () => {
    state.value = {
      caseId: '',
      currentStage: 'explore',
      stages: [],
      isRunning: false,
      status: 'pending',
    }
  }

  return {
    state,
    isAtHumanGate,
    currentStageDisplay,
    progress,
    setCaseId,
    setStage,
    setStatus,
    reset,
  }
}
