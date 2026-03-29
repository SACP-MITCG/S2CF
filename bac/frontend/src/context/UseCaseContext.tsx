import React, { createContext, useContext, useState, useCallback } from 'react'
import { ENDPOINTS } from '../config'
import type { UseCaseUI, UseCaseSummary, SectionUI, Template, TemplateSuggestion } from '../types/irm'

interface UseCaseContextType {
  // State
  useCases: UseCaseSummary[]
  currentUseCase: UseCaseUI | null
  templates: Template[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchUseCases: () => Promise<void>
  fetchUseCase: (id: string) => Promise<void>
  createUseCase: (title: string, templateId?: string) => Promise<string>
  updateUseCase: (id: string, data: Partial<UseCaseUI>) => Promise<void>
  deleteUseCase: (id: string) => Promise<void>

  // Section actions
  addSection: (useCaseId: string, type: string, title: string) => Promise<void>
  updateSection: (useCaseId: string, sectionId: string, data: Partial<SectionUI>) => Promise<void>
  deleteSection: (useCaseId: string, sectionId: string) => Promise<void>

  // Document actions
  uploadDocument: (file: File) => Promise<{ documentId: string; extraction: unknown }>
  suggestTemplate: (documentId: string) => Promise<TemplateSuggestion>

  // Utility
  clearError: () => void
}

const UseCaseContext = createContext<UseCaseContextType | undefined>(undefined)

export function UseCaseProvider({ children }: { children: React.ReactNode }) {
  const [useCases, setUseCases] = useState<UseCaseSummary[]>([])
  const [currentUseCase, setCurrentUseCase] = useState<UseCaseUI | null>(null)
  const [templates] = useState<Template[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const fetchUseCases = useCallback(async () => {
    setIsLoading(true)
    try {
      const res = await fetch(ENDPOINTS.usecases)
      if (!res.ok) throw new Error('Failed to fetch use cases')
      const data = await res.json()
      setUseCases(data.useCases || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const fetchUseCase = useCallback(async (id: string) => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.usecases}/${id}`)
      if (!res.ok) throw new Error('Failed to fetch use case')
      const data = await res.json()

      // Transform IRM JSON-LD to UI format
      const useCase: UseCaseUI = {
        id: data['@id']?.replace('urn:usecase:', '') || id,
        title: data['sacp:title'] || 'Untitled',
        description: data['sacp:description'] || '',
        templateId: data['sacp:templateId'],
        status: data['sacp:meta']?.['sacp:validationStatus'] || 'draft',
        createdAt: data['sacp:meta']?.['sacp:createdAt'],
        sections: (data['sacp:sections'] || []).map((s: Record<string, unknown>) => ({
          id: (s['@id'] as string)?.replace('urn:section:', '') || '',
          type: (s['@type'] as string)?.replace('sacp:', '') || 'Overview',
          title: s['sacp:title'] || '',
          content: s['sacp:content'] || '',
          order: s['sacp:order'] || 0,
          status: (s['sacp:meta'] as Record<string, unknown>)?.['sacp:validationStatus'] || 'draft',
          bamReferences: ((s['sacp:bamReferences'] as Record<string, unknown>[]) || []).map((ref) => ({
            id: (ref['@id'] as string)?.replace('urn:bam-ref:', '') || '',
            toolType: ref['sacp:toolType'] || 'HOPEX',
            elementId: ref['sacp:elementId'] || '',
            elementType: ref['sacp:elementType'] || '',
            elementName: ref['sacp:elementName'] || '',
            diagramId: ref['sacp:diagramId'],
            embedUrl: ref['sacp:embedUrl'],
            deepLink: ref['sacp:deepLink'],
          })),
        })),
      }

      setCurrentUseCase(useCase)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createUseCase = useCallback(async (title: string, templateId?: string): Promise<string> => {
    setIsLoading(true)
    try {
      const res = await fetch(ENDPOINTS.usecases, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, templateId }),
      })
      if (!res.ok) throw new Error('Failed to create use case')
      const data = await res.json()
      const id = data['@id']?.replace('urn:usecase:', '') || data.id
      await fetchUseCases()
      return id
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [fetchUseCases])

  const updateUseCase = useCallback(async (id: string, data: Partial<UseCaseUI>) => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.usecases}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Failed to update use case')
      await fetchUseCase(id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [fetchUseCase])

  const deleteUseCase = useCallback(async (id: string) => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.usecases}/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Failed to delete use case')
      setCurrentUseCase(null)
      await fetchUseCases()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [fetchUseCases])

  const addSection = useCallback(async (useCaseId: string, type: string, title: string) => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.usecases}/${useCaseId}/sections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, title }),
      })
      if (!res.ok) throw new Error('Failed to add section')
      await fetchUseCase(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [fetchUseCase])

  const updateSection = useCallback(async (useCaseId: string, sectionId: string, data: Partial<SectionUI>) => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.usecases}/${useCaseId}/sections/${sectionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Failed to update section')
      await fetchUseCase(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [fetchUseCase])

  const deleteSection = useCallback(async (useCaseId: string, sectionId: string) => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.usecases}/${useCaseId}/sections/${sectionId}`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error('Failed to delete section')
      await fetchUseCase(useCaseId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [fetchUseCase])

  const uploadDocument = useCallback(async (file: File) => {
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(ENDPOINTS.upload, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) throw new Error('Failed to upload document')
      return await res.json()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const suggestTemplate = useCallback(async (documentId: string): Promise<TemplateSuggestion> => {
    setIsLoading(true)
    try {
      const res = await fetch(`${ENDPOINTS.upload}/${documentId}/suggest-template`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error('Failed to get template suggestion')
      return await res.json()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  return (
    <UseCaseContext.Provider
      value={{
        useCases,
        currentUseCase,
        templates,
        isLoading,
        error,
        fetchUseCases,
        fetchUseCase,
        createUseCase,
        updateUseCase,
        deleteUseCase,
        addSection,
        updateSection,
        deleteSection,
        uploadDocument,
        suggestTemplate,
        clearError,
      }}
    >
      {children}
    </UseCaseContext.Provider>
  )
}

export function useUseCases() {
  const context = useContext(UseCaseContext)
  if (context === undefined) {
    throw new Error('useUseCases must be used within a UseCaseProvider')
  }
  return context
}
