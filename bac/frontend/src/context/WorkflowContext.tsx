import React, { createContext, useContext, useState, useCallback } from 'react'
import { ENDPOINTS } from '../config'
import type { Workflow, WorkflowProgress, WorkflowStep } from '../types/workflow'

interface WorkflowContextType {
  // State
  workflow: Workflow | null
  progress: WorkflowProgress | null
  isLoading: boolean
  error: string | null

  // Actions
  fetchWorkflow: (useCaseId: string) => Promise<void>
  fetchProgress: (useCaseId: string) => Promise<void>
  initializeWorkflow: (useCaseId: string) => Promise<void>
  executeStep: (useCaseId: string, stepNumber: number) => Promise<void>
  completeStep: (useCaseId: string, stepNumber: number, outputData?: Record<string, unknown>) => Promise<void>
  approveStep: (useCaseId: string, stepNumber: number, reviewerId: string, notes?: string) => Promise<void>
  rejectStep: (useCaseId: string, stepNumber: number, reviewerId: string, notes: string) => Promise<void>
  advanceWorkflow: (useCaseId: string) => Promise<void>
  fetchStep: (useCaseId: string, stepNumber: number) => Promise<WorkflowStep | null>
  clearError: () => void
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined)

export function WorkflowProvider({ children }: { children: React.ReactNode }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null)
  const [progress, setProgress] = useState<WorkflowProgress | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  /** Helper: call workflow API with graceful fallback */
  const workflowFetch = useCallback(async (url: string, options?: RequestInit) => {
    const res = await fetch(url, options)
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.error || `Workflow API error (${res.status})`)
    }
    return res.json()
  }, [])

  const fetchWorkflow = useCallback(async (useCaseId: string) => {
    setIsLoading(true)
    try {
      const data = await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow`)
      setWorkflow(data)
    } catch (err) {
      // Graceful fallback — workflow endpoints may not exist yet
      setWorkflow(null)
      setError(err instanceof Error ? err.message : 'Workflow not available')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch])

  const fetchProgress = useCallback(async (useCaseId: string) => {
    try {
      const data = await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/progress`)
      setProgress(data)
    } catch {
      setProgress(null)
    }
  }, [workflowFetch])

  const initializeWorkflow = useCallback(async (useCaseId: string) => {
    setIsLoading(true)
    try {
      const data = await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      setWorkflow(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize workflow')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch])

  const executeStep = useCallback(async (useCaseId: string, stepNumber: number) => {
    setIsLoading(true)
    try {
      await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/steps/${stepNumber}/execute`, {
        method: 'POST',
      })
      await fetchWorkflow(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute step')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch, fetchWorkflow])

  const completeStep = useCallback(async (useCaseId: string, stepNumber: number, outputData?: Record<string, unknown>) => {
    setIsLoading(true)
    try {
      await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/steps/${stepNumber}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ outputData: outputData || {} }),
      })
      await fetchWorkflow(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete step')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch, fetchWorkflow])

  const approveStep = useCallback(async (useCaseId: string, stepNumber: number, reviewerId: string, notes?: string) => {
    setIsLoading(true)
    try {
      await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/steps/${stepNumber}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'approve', reviewerId, notes }),
      })
      await fetchWorkflow(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve step')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch, fetchWorkflow])

  const rejectStep = useCallback(async (useCaseId: string, stepNumber: number, reviewerId: string, notes: string) => {
    setIsLoading(true)
    try {
      await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/steps/${stepNumber}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'reject', reviewerId, notes }),
      })
      await fetchWorkflow(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject step')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch, fetchWorkflow])

  const advanceWorkflow = useCallback(async (useCaseId: string) => {
    setIsLoading(true)
    try {
      await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/advance`, {
        method: 'POST',
      })
      await fetchWorkflow(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to advance workflow')
    } finally {
      setIsLoading(false)
    }
  }, [workflowFetch, fetchWorkflow])

  const fetchStep = useCallback(async (useCaseId: string, stepNumber: number): Promise<WorkflowStep | null> => {
    try {
      return await workflowFetch(`${ENDPOINTS.usecases}/${useCaseId}/workflow/steps/${stepNumber}`)
    } catch {
      return null
    }
  }, [workflowFetch])

  return (
    <WorkflowContext.Provider
      value={{
        workflow,
        progress,
        isLoading,
        error,
        fetchWorkflow,
        fetchProgress,
        initializeWorkflow,
        executeStep,
        completeStep,
        approveStep,
        rejectStep,
        advanceWorkflow,
        fetchStep,
        clearError,
      }}
    >
      {children}
    </WorkflowContext.Provider>
  )
}

export function useWorkflow() {
  const context = useContext(WorkflowContext)
  if (context === undefined) {
    throw new Error('useWorkflow must be used within a WorkflowProvider')
  }
  return context
}
