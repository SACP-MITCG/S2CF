// Workflow types aligned with backend app/models/workflow.py
// These types define the contract that backend implementers must match.

export type WorkflowStepType =
  | 'requirements'    // Step 1: Ingest requirements document
  | 'blueprint'       // Step 2: Match to Catena-X use case blueprint
  | 'reference_arch'  // Step 3: Incorporate Tractus-X reference architecture
  | 'landscape'       // Step 4: Incorporate digital landscape (HOPEX read)
  | 'export'          // Step 5: Export to HOPEX

export type WorkflowStepStatus =
  | 'pending'
  | 'in_progress'
  | 'awaiting_review'
  | 'completed'
  | 'failed'
  | 'skipped'
  | 'rolled_back'

export type WorkflowStatus = 'not_started' | 'in_progress' | 'completed' | 'failed'

export interface WorkflowStep {
  id: string
  useCaseId: string
  stepNumber: number
  stepType: WorkflowStepType
  status: WorkflowStepStatus
  inputData: Record<string, unknown>
  outputData: Record<string, unknown>
  errorData: Record<string, unknown>
  startedAt: string | null
  completedAt: string | null
  executedBy: string
  requiresReview: boolean
  reviewedBy: string | null
  reviewedAt: string | null
  reviewNotes: string | null
  createdAt: string | null
}

export interface WorkflowStepSummary {
  id: string
  stepNumber: number
  stepType: WorkflowStepType
  status: WorkflowStepStatus
  requiresReview: boolean
  completedAt: string | null
}

export interface Workflow {
  id: string
  useCaseId: string
  currentStep: number
  status: WorkflowStatus
  startedAt: string | null
  completedAt: string | null
  steps: WorkflowStepSummary[]
  createdAt: string | null
}

export interface WorkflowProgress {
  totalSteps: number
  completedSteps: number
  awaitingReview: number
  currentStep: number
  percentComplete: number
  status: WorkflowStatus
}

// Human-readable labels for workflow steps
export const WORKFLOW_STEP_LABELS: Record<WorkflowStepType, string> = {
  requirements: 'Requirements',
  blueprint: 'Blueprint',
  reference_arch: 'Reference Architecture',
  landscape: 'Digital Landscape',
  export: 'Export',
}

export const WORKFLOW_STEP_DESCRIPTIONS: Record<WorkflowStepType, string> = {
  requirements: 'Ingest and extract requirements from uploaded documents',
  blueprint: 'Match to Catena-X or INOVIA use case blueprint',
  reference_arch: 'Incorporate Tractus-X reference architecture and standards',
  landscape: 'Import digital landscape from HOPEX / EA tools',
  export: 'Export validated use case to HOPEX / documentation',
}

// Which steps require HITL review (matches backend HITL_REQUIRED_STEPS)
export const HITL_REQUIRED_STEPS: Set<WorkflowStepType> = new Set([
  'requirements',
  'blueprint',
  'reference_arch',
])

// Maps workflow steps to the GitHub tickets that implement them
export const WORKFLOW_STEP_TICKETS: Record<WorkflowStepType, string[]> = {
  requirements: ['#8 Identify digital landscape'],
  blueprint: ['#6 Find use case blueprints', '#11 Align with Catena-X'],
  reference_arch: ['#7 Use existing standards', '#9 Co-Create Architecture Design'],
  landscape: ['#8 Identify digital landscape', '#9 Co-Create Architecture Design'],
  export: ['#10 Use case documentation', '#9 Co-Create Architecture Design'],
}
