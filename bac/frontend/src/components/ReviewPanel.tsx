import { useState } from 'react'
import { CheckCircle2, XCircle, MessageSquare, Clock, User } from 'lucide-react'
import type { WorkflowStep } from '../types/workflow'
import { WORKFLOW_STEP_LABELS, type WorkflowStepType } from '../types/workflow'

interface ReviewPanelProps {
  /** The workflow step awaiting review, or null to show placeholder */
  step: WorkflowStep | null
  onApprove: (reviewerId: string, notes?: string) => void
  onReject: (reviewerId: string, notes: string) => void
  onClose: () => void
}

export default function ReviewPanel({ step, onApprove, onReject, onClose }: ReviewPanelProps) {
  const [reviewNotes, setReviewNotes] = useState('')
  const [reviewerId] = useState('current-user') // Placeholder until auth exists

  if (!step) {
    return (
      <div className="p-6 border-t border-border bg-card/50">
        <p className="text-sm text-muted-foreground text-center">
          No steps awaiting review
        </p>
      </div>
    )
  }

  const stepLabel = WORKFLOW_STEP_LABELS[step.stepType as WorkflowStepType] || step.stepType
  const isAwaitingReview = step.status === 'awaiting_review'
  const isReviewed = step.reviewedBy !== null

  return (
    <div className="border-t border-border bg-card/50">
      {/* Review Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-amber-500" />
          <h3 className="text-sm font-medium">
            Review: Step {step.stepNumber} — {stepLabel}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          Close
        </button>
      </div>

      {/* Review Content */}
      <div className="p-6 space-y-4">
        {/* Step output summary */}
        {step.outputData && Object.keys(step.outputData).length > 0 && (
          <div className="p-3 rounded-sm bg-muted/50 border border-border">
            <p className="text-xs font-medium text-muted-foreground mb-2">Step Output</p>
            <pre className="text-xs text-foreground overflow-auto max-h-32">
              {JSON.stringify(step.outputData, null, 2)}
            </pre>
          </div>
        )}

        {/* Previous review info */}
        {isReviewed && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <User className="w-3 h-3" />
              Reviewed by: {step.reviewedBy}
            </span>
            {step.reviewedAt && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {new Date(step.reviewedAt).toLocaleString()}
              </span>
            )}
            {step.reviewNotes && (
              <span className="flex-1 truncate">Notes: {step.reviewNotes}</span>
            )}
          </div>
        )}

        {/* Review form */}
        {isAwaitingReview && (
          <>
            <div>
              <label className="text-xs font-medium text-muted-foreground block mb-1.5">
                Review Notes
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Add rationale for your decision..."
                className="w-full h-20 p-3 rounded-sm border border-border bg-card resize-none outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-sm"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => onApprove(reviewerId, reviewNotes || undefined)}
                className="flex items-center gap-2 px-4 py-2 rounded-sm bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 transition-colors text-sm font-medium"
              >
                <CheckCircle2 className="w-4 h-4" />
                Approve
              </button>
              <button
                onClick={() => {
                  if (!reviewNotes.trim()) {
                    alert('Please provide a reason for rejection')
                    return
                  }
                  onReject(reviewerId, reviewNotes)
                }}
                className="flex items-center gap-2 px-4 py-2 rounded-sm bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors text-sm font-medium"
              >
                <XCircle className="w-4 h-4" />
                Reject
              </button>
              <p className="text-[10px] text-muted-foreground flex-1">
                Rejection requires a rationale note.
              </p>
            </div>
          </>
        )}

        {/* Non-reviewable state */}
        {!isAwaitingReview && !isReviewed && (
          <p className="text-sm text-muted-foreground">
            This step is not awaiting review. Current status: <strong>{step.status}</strong>
          </p>
        )}
      </div>
    </div>
  )
}
