import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Building2, FileText, ChevronRight, Save, Trash2 } from 'lucide-react'
import { useUseCases } from '../context/UseCaseContext'
import { useToast } from '../context/ToastContext'
import { useWorkflow } from '../context/WorkflowContext'
import { useHopex } from '../context/HopexContext'
import type { SectionUI } from '../types/irm'
import type { WorkflowStep } from '../types/workflow'

// Decomposed components
import SectionSidebar from '../components/SectionSidebar'
import SectionEditor from '../components/SectionEditor'
import HopexPanel from '../components/HopexPanel'
import ExportMenu from '../components/ExportMenu'
import WorkflowStepper from '../components/WorkflowStepper'
import ReviewPanel from '../components/ReviewPanel'

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

export default function Editor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentUseCase, fetchUseCase, updateSection, addSection, deleteSection, isLoading } = useUseCases()
  const { addToast } = useToast()

  const {
    workflow,
    fetchWorkflow,
    initializeWorkflow,
    approveStep,
    rejectStep,
    fetchStep,
  } = useWorkflow()
  const { linkElement, unlinkElement } = useHopex()

  const [activeSection, setActiveSection] = useState<string | null>(null)
  const [editingContent, setEditingContent] = useState('')
  const [showHopexPanel, setShowHopexPanel] = useState(false)
  const [reviewStep, setReviewStep] = useState<WorkflowStep | null>(null)
  const [showReviewPanel, setShowReviewPanel] = useState(false)

  // Fetch use case and workflow on mount
  useEffect(() => {
    if (id) {
      fetchUseCase(id)
      fetchWorkflow(id)
    }
  }, [id, fetchUseCase, fetchWorkflow])

  useEffect(() => {
    if (currentUseCase?.sections?.length && !activeSection) {
      setActiveSection(currentUseCase.sections[0].id)
      setEditingContent(currentUseCase.sections[0].content)
    }
  }, [currentUseCase, activeSection])

  const activeSectionData = currentUseCase?.sections?.find((s) => s.id === activeSection)

  const handleSectionClick = useCallback(
    (section: SectionUI) => {
      // Auto-save current section before switching
      if (activeSection && id && editingContent !== activeSectionData?.content) {
        updateSection(id, activeSection, { content: editingContent })
      }
      setActiveSection(section.id)
      setEditingContent(section.content)
    },
    [activeSection, id, editingContent, activeSectionData, updateSection]
  )

  const handleSave = useCallback(async () => {
    if (!id || !activeSection) return
    try {
      await updateSection(id, activeSection, { content: editingContent })
      addToast('Saved', 'success')
    } catch {
      addToast('Failed to save', 'error')
    }
  }, [id, activeSection, editingContent, updateSection, addToast])

  const handleAddSection = useCallback(async () => {
    if (!id) return
    try {
      await addSection(id, 'CustomSection', 'New Section')
      addToast('Section added', 'success')
    } catch {
      addToast('Failed to add section', 'error')
    }
  }, [id, addSection, addToast])

  const handleDeleteSection = useCallback(
    async (sectionId: string) => {
      if (!id) return
      if (!confirm('Delete this section?')) return
      try {
        await deleteSection(id, sectionId)
        setActiveSection(null)
        addToast('Section deleted', 'success')
      } catch {
        addToast('Failed to delete section', 'error')
      }
    },
    [id, deleteSection, addToast]
  )

  const handleTitleChange = useCallback(
    (title: string) => {
      if (id && activeSection) {
        updateSection(id, activeSection, { title })
      }
    },
    [id, activeSection, updateSection]
  )

  const handleLinkElement = useCallback(
    async (element: { id: string; name: string; type: string }) => {
      if (!id || !activeSection) {
        addToast('Select a section first', 'info')
        return
      }
      const ok = await linkElement(id, activeSection, element as import('../types/irm').HopexElement)
      if (ok) {
        await fetchUseCase(id)
        addToast(`Linked: ${element.name}`, 'success')
      } else {
        addToast(`Link endpoint not available yet — ${element.name} (${element.type})`, 'info')
      }
    },
    [id, activeSection, linkElement, fetchUseCase, addToast]
  )

  const handleUnlinkBAMReference = useCallback(
    async (refId: string) => {
      if (!id || !activeSection) return
      const ok = await unlinkElement(id, activeSection, refId)
      if (ok) {
        await fetchUseCase(id)
        addToast('Unlinked', 'success')
      } else {
        addToast('Unlink endpoint not available yet', 'info')
      }
    },
    [id, activeSection, unlinkElement, fetchUseCase, addToast]
  )

  // Workflow handlers
  const handleStepClick = useCallback(
    async (stepNumber: number) => {
      if (!id) return
      // If step 0 is clicked via placeholder, initialize the workflow
      if (stepNumber === 0 && !workflow) {
        await initializeWorkflow(id)
        return
      }
      // Fetch full step data to check if it's awaiting review
      const step = await fetchStep(id, stepNumber)
      if (step?.status === 'awaiting_review') {
        setReviewStep(step)
        setShowReviewPanel(true)
      }
    },
    [id, workflow, initializeWorkflow, fetchStep]
  )

  const handleApproveStep = useCallback(
    async (reviewerId: string, notes?: string) => {
      if (!id || !reviewStep) return
      await approveStep(id, reviewStep.stepNumber, reviewerId, notes)
      setShowReviewPanel(false)
      setReviewStep(null)
      addToast(`Step ${reviewStep.stepNumber} approved`, 'success')
    },
    [id, reviewStep, approveStep, addToast]
  )

  const handleRejectStep = useCallback(
    async (reviewerId: string, notes: string) => {
      if (!id || !reviewStep) return
      await rejectStep(id, reviewStep.stepNumber, reviewerId, notes)
      setShowReviewPanel(false)
      setReviewStep(null)
      addToast(`Step ${reviewStep.stepNumber} rejected`, 'info')
    },
    [id, reviewStep, rejectStep, addToast]
  )

  // Loading state
  if (isLoading && !currentUseCase) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Loading...
      </div>
    )
  }

  // Not found state
  if (!currentUseCase) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">Use case not found</p>
          <button onClick={() => navigate('/')} className="btn-secondary">
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full">
      {/* Left: Section Sidebar */}
      <SectionSidebar
        title={currentUseCase.title}
        sections={currentUseCase.sections}
        activeSection={activeSection}
        onSectionClick={handleSectionClick}
        onAddSection={handleAddSection}
        onBack={() => navigate('/')}
      />

      {/* Center: Main Editor */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Workflow Stepper */}
        <WorkflowStepper
          steps={workflow?.steps || []}
          currentStep={workflow?.currentStep || 1}
          onStepClick={handleStepClick}
        />

        {/* Editor Header */}
        <header className="flex items-center justify-between h-14 px-6 border-b border-border bg-background/50">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileText className="w-4 h-4" />
            <span>{activeSectionData?.title || 'Select a section'}</span>
            {activeSectionData && (
              <>
                <ChevronRight className="w-3 h-3" />
                <span className="text-xs">{sectionTypeLabels[activeSectionData.type]}</span>
              </>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHopexPanel(!showHopexPanel)}
              className={`btn-ghost ${showHopexPanel ? 'bg-primary/10 text-primary' : ''}`}
            >
              <Building2 className="w-4 h-4" />
              HOPEX
            </button>

            <button onClick={handleSave} className="btn-ghost">
              <Save className="w-4 h-4" />
              Save
            </button>

            <ExportMenu useCaseId={id!} useCaseTitle={currentUseCase.title} />

            {activeSection && (
              <button
                onClick={() => handleDeleteSection(activeSection)}
                className="btn-ghost text-destructive hover:text-destructive"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </header>

        {/* Editor Content */}
        <div className="flex-1 overflow-auto">
          {activeSectionData ? (
            <SectionEditor
              section={activeSectionData}
              editingContent={editingContent}
              onContentChange={setEditingContent}
              onTitleChange={handleTitleChange}
              onSave={handleSave}
              onUnlinkBAMReference={handleUnlinkBAMReference}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Select a section to edit
            </div>
          )}
        </div>

        {/* Review Panel (shown when a step is selected for review) */}
        {showReviewPanel && (
          <ReviewPanel
            step={reviewStep}
            onApprove={handleApproveStep}
            onReject={handleRejectStep}
            onClose={() => {
              setShowReviewPanel(false)
              setReviewStep(null)
            }}
          />
        )}
      </div>

      {/* Right: HOPEX Panel */}
      <HopexPanel
        visible={showHopexPanel}
        onClose={() => setShowHopexPanel(false)}
        onLinkElement={handleLinkElement}
      />
    </div>
  )
}
