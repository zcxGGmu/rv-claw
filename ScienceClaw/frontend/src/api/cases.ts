import type { Case, CreateCaseRequest, ListCasesParams, PaginatedCases } from '@/types/case'
import type { ReviewDecision, ReviewRecord } from '@/types/review'
import type { Artifact } from '@/types/artifact'
import type { AgentEvent, SSECallbacks } from '@/types/event'
import { apiClient } from './client'

export async function createCase(data: CreateCaseRequest): Promise<Case> {
  const response = await apiClient.post<Case>('/cases', data)
  return response.data
}

export async function listCases(params?: ListCasesParams): Promise<PaginatedCases> {
  const response = await apiClient.get<PaginatedCases>('/cases', { params })
  return response.data
}

export async function getCase(caseId: string): Promise<Case> {
  const response = await apiClient.get<Case>(`/cases/${caseId}`)
  return response.data
}

export async function deleteCase(caseId: string): Promise<void> {
  await apiClient.delete(`/cases/${caseId}`)
}

export async function startPipeline(caseId: string): Promise<void> {
  await apiClient.post(`/cases/${caseId}/start`)
}

export async function submitReview(caseId: string, decision: ReviewDecision): Promise<void> {
  await apiClient.post(`/cases/${caseId}/review`, decision)
}

export async function getArtifacts(
  caseId: string,
  stage: string,
  round?: number,
): Promise<Artifact[]> {
  const response = await apiClient.get<Artifact[]>(`/cases/${caseId}/artifacts`, {
    params: { stage, round },
  })
  return response.data
}

export async function getHistory(caseId: string): Promise<ReviewRecord[]> {
  const response = await apiClient.get<ReviewRecord[]>(`/cases/${caseId}/history`)
  return response.data
}

export function subscribeCaseEvents(
  caseId: string,
  callbacks: SSECallbacks,
): () => void {
  const eventSource = new EventSource(`/api/v1/cases/${caseId}/events`)

  eventSource.onmessage = (event) => {
    const data: AgentEvent = JSON.parse(event.data)

    switch (data.event_type) {
      case 'stage_change':
        callbacks.onStageChange?.(data.data.stage as string, data.data.status as string)
        break
      case 'agent_output':
        callbacks.onAgentOutput?.(data.data.type as string, data.data.content as string)
        break
      case 'review_request':
        callbacks.onReviewRequest?.(data.data.stage as string, data.data.artifact_ref as string)
        break
      case 'iteration_update':
        callbacks.onIterationUpdate?.(data.data.iteration as number)
        break
      case 'cost_update':
        callbacks.onCostUpdate?.(data.data.cost as number)
        break
      case 'error':
        callbacks.onError?.(data.data.message as string)
        break
      case 'completed':
        callbacks.onCompleted?.()
        break
    }
  }

  eventSource.onerror = () => {
    callbacks.onError?.('SSE connection error')
  }

  return () => {
    eventSource.close()
  }
}
