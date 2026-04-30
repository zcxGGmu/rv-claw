import type { ReviewVerdict } from '@/types/review'
import { client } from './client'

export async function getReviewVerdict(
  caseId: string,
  iteration: number,
): Promise<ReviewVerdict> {
  const response = await client.get<ReviewVerdict>(`/cases/${caseId}/reviews/${iteration}`)
  return response.data
}
