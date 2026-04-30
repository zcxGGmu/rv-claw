export interface Artifact {
  id: string
  case_id: string
  stage: string
  round_num?: number
  filename: string
  path: string
  content_type: string
  size: number
  created_at: string
}

export type ArtifactType = 'json' | 'patch' | 'log' | 'report' | 'diff'
