import { CheckCircle2, Circle, Clock, AlertCircle, Eye, SkipForward, RotateCcw } from 'lucide-react'
import type { WorkflowStepSummary, WorkflowStepStatus, WorkflowStepType } from '../types/workflow'
import { WORKFLOW_STEP_LABELS, WORKFLOW_STEP_DESCRIPTIONS, HITL_REQUIRED_STEPS } from '../types/workflow'

interface WorkflowStepperProps {
  steps: WorkflowStepSummary[]
  currentStep: number
  onStepClick?: (stepNumber: number) => void
}

const statusIcons: Record<WorkflowStepStatus, typeof Circle> = {
  pending: Circle,
  in_progress: Clock,
  awaiting_review: Eye,
  completed: CheckCircle2,
  failed: AlertCircle,
  skipped: SkipForward,
  rolled_back: RotateCcw,
}

const statusColors: Record<WorkflowStepStatus, string> = {
  pending: 'text-muted-foreground',
  in_progress: 'text-blue-500',
  awaiting_review: 'text-amber-500',
  completed: 'text-emerald-500',
  failed: 'text-destructive',
  skipped: 'text-muted-foreground',
  rolled_back: 'text-muted-foreground',
}

const statusBgColors: Record<WorkflowStepStatus, string> = {
  pending: 'bg-muted',
  in_progress: 'bg-blue-500/10',
  awaiting_review: 'bg-amber-500/10',
  completed: 'bg-emerald-500/10',
  failed: 'bg-destructive/10',
  skipped: 'bg-muted',
  rolled_back: 'bg-muted',
}

export default function WorkflowStepper({ steps, currentStep, onStepClick }: WorkflowStepperProps) {
  if (steps.length === 0) {
    return (
      <WorkflowPlaceholder onInitialize={onStepClick ? () => onStepClick(0) : undefined} />
    )
  }

  return (
    <div className="flex items-center gap-1 px-6 py-3 border-b border-border bg-card/30 overflow-x-auto">
      {steps.map((step, index) => {
        const Icon = statusIcons[step.status] || Circle
        const isActive = step.stepNumber === currentStep
        const requiresHITL = HITL_REQUIRED_STEPS.has(step.stepType as WorkflowStepType)

        return (
          <div key={step.id} className="flex items-center">
            {/* Step */}
            <button
              onClick={() => onStepClick?.(step.stepNumber)}
              className={`
                flex items-center gap-2 px-3 py-2 rounded-sm transition-colors text-left
                ${isActive ? 'bg-primary/10 ring-1 ring-primary/30' : 'hover:bg-muted'}
                ${onStepClick ? 'cursor-pointer' : 'cursor-default'}
              `}
              title={WORKFLOW_STEP_DESCRIPTIONS[step.stepType as WorkflowStepType]}
            >
              <div className={`flex items-center justify-center w-6 h-6 rounded-full ${statusBgColors[step.status]}`}>
                <Icon className={`w-3.5 h-3.5 ${statusColors[step.status]}`} />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium truncate">
                  {WORKFLOW_STEP_LABELS[step.stepType as WorkflowStepType] || step.stepType}
                </p>
                <p className="text-[10px] text-muted-foreground truncate">
                  {step.status === 'awaiting_review'
                    ? 'Awaiting review'
                    : step.status.replace('_', ' ')}
                  {requiresHITL && step.status === 'pending' && ' (HITL)'}
                </p>
              </div>
            </button>

            {/* Connector line between steps */}
            {index < steps.length - 1 && (
              <div className={`w-4 h-px mx-0.5 ${
                step.status === 'completed' ? 'bg-emerald-500/50' : 'bg-border'
              }`} />
            )}
          </div>
        )
      })}
    </div>
  )
}

/** Shown when no workflow exists yet */
function WorkflowPlaceholder({ onInitialize }: { onInitialize?: () => void }) {
  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-border bg-card/30">
      <div className="flex items-center gap-3">
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
              <span className="text-[10px] text-muted-foreground">{n}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          5-step workflow: Requirements → Blueprint → Reference Arch → Landscape → Export
        </p>
      </div>
      {onInitialize && (
        <button onClick={onInitialize} className="btn-ghost text-xs">
          Initialize Workflow
        </button>
      )}
    </div>
  )
}
