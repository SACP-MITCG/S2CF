import { ArrowLeft, GripVertical, Plus } from 'lucide-react'
import type { SectionUI } from '../types/irm'
import StatusBadge from './StatusBadge'

const sectionTypeLabels: Record<string, string> = {
  Overview: 'Overview',
  BusinessContext: 'Business Context',
  SMARTObjective: 'Objectives',
  UserJourney: 'User Journeys',
  Assumptions: 'Assumptions',
  OpenQuestions: 'Open Questions',
  BAMReferences: 'Architecture',
  ValidationStatus: 'Validation',
  CustomSection: 'Custom',
}

interface SectionSidebarProps {
  title: string
  sections: SectionUI[]
  activeSection: string | null
  onSectionClick: (section: SectionUI) => void
  onAddSection: () => void
  onBack: () => void
}

export default function SectionSidebar({
  title,
  sections,
  activeSection,
  onSectionClick,
  onAddSection,
  onBack,
}: SectionSidebarProps) {
  return (
    <aside className="w-64 flex-shrink-0 border-r border-border bg-card/30 flex flex-col">
      <div className="flex items-center gap-2 p-4 border-b border-border">
        <button
          onClick={onBack}
          className="p-1.5 rounded-sm hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <h2 className="text-sm font-medium truncate flex-1">{title}</h2>
      </div>

      <div className="flex-1 overflow-auto p-3 space-y-1">
        {sections.map((section, index) => (
          <div
            key={section.id}
            onClick={() => onSectionClick(section)}
            className={`section-card animate-slide-in-left stagger-${(index % 5) + 1} ${
              activeSection === section.id ? 'active' : ''
            }`}
          >
            <GripVertical className="w-3 h-3 text-muted-foreground/50 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate">{section.title}</p>
              <p className="text-[10px] text-muted-foreground">
                {sectionTypeLabels[section.type] || section.type}
              </p>
            </div>
            <StatusBadge status={section.status} />
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-border">
        <button
          onClick={onAddSection}
          className="btn-ghost w-full justify-center"
        >
          <Plus className="w-4 h-4" />
          Add Section
        </button>
      </div>
    </aside>
  )
}
