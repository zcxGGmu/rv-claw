import { apiClient } from './client'

export async function downloadArtifact(caseId: string, path: string): Promise<Blob> {
  const response = await apiClient.get(`/cases/${caseId}/artifacts/download`, {
    params: { path },
    responseType: 'blob',
  })
  return response.data
}

export async function getArtifactContent(caseId: string, path: string): Promise<string> {
  const response = await apiClient.get<string>(`/cases/${caseId}/artifacts/content`, {
    params: { path },
  })
  return response.data
}
