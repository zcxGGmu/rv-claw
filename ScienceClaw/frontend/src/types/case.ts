export type CaseStatus =
  | 'created'
  | 'exploring'
  | 'pending_explore_review'
  | 'planning'
  | 'pending_plan_review'
  | 'developing'
  | 'reviewing'
  | 'pending_code_review'
  | 'testing'
  | 'pending_test_review'
  | 'completed'
  | 'abandoned'
  | 'escalated'

export interface Case {
  id: string
  title: string
  status: CaseStatus
  target_repo: string
  input_context: string
  contribution_type?: string
  review_iterations: number
  max_review_iterations: number
  cost: {
    input_tokens: number
    output_tokens: number
    estimated_usd: number
  }
  created_by: string
  created_at: string
  updated_at: string
}

export interface CreateCaseRequest {
  title: string
  target_repo: string
  input_context: string
  contribution_type?: string
}

export interface ListCasesParams {
  status?: CaseStatus
  target_repo?: string
  search?: string
  page?: number
  page_size?: number
}

export interface PaginatedCases {
  items: Case[]
  total: number
  page: number
  page_size: number
  pages: number
}
