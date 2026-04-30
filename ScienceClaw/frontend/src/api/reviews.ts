import type { ReviewDecision, ReviewRecord, ReviewVerdict } from '@/types/review'
import { apiClient } from './client'

export async function submitReview(caseId: string, decision: ReviewDecision): Promise<void> {
  await apiClient.post(`/cases/${caseId}/review`, decision)
}

export async function getHistory(caseId: string): Promise<ReviewRecord[]> {
  const response = await apiClient.get<ReviewRecord[]>(`/cases/${caseId}/history`)
  return response.data
}

export async function getReviewVerdict(caseId: string): Promise<ReviewVerdict | null> {
  try {
    const response = await apiClient.get<ReviewVerdict>(`/cases/${caseId}/review/verdict`)
    return response.data
  } catch {
    return null
  }
}
