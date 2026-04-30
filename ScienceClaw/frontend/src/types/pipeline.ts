export interface PipelineStage {
  id: string
  case_id: string
  stage_type: StageType
  status: StageStatus
  started_at?: string
  completed_at?: string
  error?: string
}

export type StageType = 'explore' | 'plan' | 'develop' | 'review' | 'test'

export type StageStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

export interface PipelineState {
  case_id: string
  current_stage: StageType
  stages: PipelineStage[]
  review_iterations: number
  max_review_iterations: number
  pending_approval_stage?: string
  total_input_tokens: number
  total_output_tokens: number
  estimated_cost_usd: number
}
