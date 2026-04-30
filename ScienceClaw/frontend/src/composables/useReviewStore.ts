import { ref, computed } from 'vue'
import type { ReviewVerdict, ReviewFinding } from '@/contracts/review'

export interface ReviewState {
  verdict: ReviewVerdict | null
  isSubmitting: boolean
  error: string | null
}

export function useReviewStore() {
  const state = ref<ReviewState>({
    verdict: null,
    isSubmitting: false,
    error: null,
  })

  const hasVerdict = computed(() => state.value.verdict !== null)
  
  const isApproved = computed(() => {
    return state.value.verdict?.approved ?? false
  })

  const findingsBySeverity = computed(() => {
    if (!state.value.verdict) return {}
    
    const groups: Record<string, ReviewFinding[]> = {
      critical: [],
      major: [],
      minor: [],
      suggestion: [],
    }
    
    state.value.verdict.findings.forEach(finding => {
      if (groups[finding.severity]) {
        groups[finding.severity].push(finding)
      }
    })
    
    return groups
  })

  const criticalCount = computed(() => findingsBySeverity.value.critical.length)
  const majorCount = computed(() => findingsBySeverity.value.major.length)
  const minorCount = computed(() => findingsBySeverity.value.minor.length)

  const setVerdict = (verdict: ReviewVerdict) => {
    state.value.verdict = verdict
  }

  const setSubmitting = (submitting: boolean) => {
    state.value.isSubmitting = submitting
  }

  const setError = (error: string | null) => {
    state.value.error = error
  }

  const reset = () => {
    state.value = {
      verdict: null,
      isSubmitting: false,
      error: null,
    }
  }

  return {
    state,
    hasVerdict,
    isApproved,
    findingsBySeverity,
    criticalCount,
    majorCount,
    minorCount,
    setVerdict,
    setSubmitting,
    setError,
    reset,
  }
}
