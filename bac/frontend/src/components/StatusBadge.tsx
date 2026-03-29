import type { SectionStatus } from '../types/irm'

const statusConfig: Record<SectionStatus, { label: string; class: string }> = {
  draft: { label: 'Draft', class: 'badge-draft' },
  in_review: { label: 'Review', class: 'badge-in-review' },
  approved: { label: 'Approved', class: 'badge-approved' },
  rejected: { label: 'Rejected', class: 'badge-rejected' },
}

interface StatusBadgeProps {
  status: SectionStatus
  /** Show dot indicator (used in Dashboard cards) */
  showDot?: boolean
  /** Additional CSS classes */
  className?: string
}

export default function StatusBadge({ status, showDot = false, className = '' }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.draft
  return (
    <span className={`badge-status ${config.class} ${showDot ? '' : 'text-[10px] px-2 py-0.5'} ${className}`}>
      {showDot && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
      {config.label}
    </span>
  )
}
