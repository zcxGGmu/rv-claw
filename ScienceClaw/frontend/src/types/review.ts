export interface ReviewDecision {
  action: 'approve' | 'reject' | 'reject_to' | 'modify' | 'abandon'
  comment?: string
  reject_to_stage?: string
  modified_artifacts?: Record<string, string>
}

export interface ReviewVerdict {
  approved: boolean
  findings: ReviewFinding[]
  reviewer_model: string
  iteration: number
}

export interface ReviewFinding {
  severity: 'critical' | 'major' | 'minor' | 'info'
  category: string
  description: string
  line_number?: number
  file_path?: string
}

export interface ReviewRecord {
  id: string
  case_id: string
  stage: string
  action: string
  comment?: string
  reviewer: string
  created_at: string
}
