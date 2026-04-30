import { ref, computed } from 'vue'
import type { Case, CreateCaseRequest, ListCasesParams } from '@/types/case'
import { createCase, listCases, getCase, deleteCase, startPipeline } from '@/api/cases'

export function useCaseStore() {
  const cases = ref<Case[]>([])
  const currentCase = ref<Case | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  const hasCases = computed(() => cases.value.length > 0)
  const runningCases = computed(() => cases.value.filter(c => c.status === 'running'))
  const pendingCases = computed(() => cases.value.filter(c => c.status === 'pending'))

  const fetchCases = async (params?: ListCasesParams) => {
    loading.value = true
    error.value = null
    try {
      const response = await listCases(params)
      cases.value = response.cases
      totalCount.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch cases'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCase = async (caseId: string) => {
    loading.value = true
    error.value = null
    try {
      const caseData = await getCase(caseId)
      currentCase.value = caseData
      return caseData
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch case'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createNewCase = async (data: CreateCaseRequest) => {
    loading.value = true
    error.value = null
    try {
      const newCase = await createCase(data)
      cases.value.unshift(newCase)
      totalCount.value++
      return newCase
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create case'
      throw err
    } finally {
      loading.value = false
    }
  }

  const removeCase = async (caseId: string) => {
    loading.value = true
    error.value = null
    try {
      await deleteCase(caseId)
      cases.value = cases.value.filter(c => c.id !== caseId)
      totalCount.value--
      if (currentCase.value?.id === caseId) {
        currentCase.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete case'
      throw err
    } finally {
      loading.value = false
    }
  }

  const startCasePipeline = async (caseId: string) => {
    loading.value = true
    error.value = null
    try {
      await startPipeline(caseId)
      const caseIndex = cases.value.findIndex(c => c.id === caseId)
      if (caseIndex !== -1) {
        cases.value[caseIndex].status = 'running'
      }
      if (currentCase.value?.id === caseId) {
        currentCase.value.status = 'running'
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to start pipeline'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCaseStatus = (caseId: string, status: string) => {
    const caseItem = cases.value.find(c => c.id === caseId)
    if (caseItem) {
      caseItem.status = status
    }
    if (currentCase.value?.id === caseId) {
      currentCase.value.status = status
    }
  }

  return {
    cases,
    currentCase,
    loading,
    error,
    totalCount,
    hasCases,
    runningCases,
    pendingCases,
    fetchCases,
    fetchCase,
    createNewCase,
    removeCase,
    startCasePipeline,
    updateCaseStatus,
  }
}
