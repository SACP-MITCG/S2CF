import React, { createContext, useContext, useState, useCallback } from 'react'
import { ENDPOINTS, bamReferenceUrl } from '../config'
import type { HopexElement } from '../types/irm'

type ConnectionStatus = 'connected' | 'disconnected' | 'loading'

interface HopexContextType {
  // State
  elements: HopexElement[]
  connectionStatus: ConnectionStatus
  isLoading: boolean

  // Actions
  fetchElements: () => Promise<void>
  searchElements: (query: string, type?: string) => Promise<HopexElement[]>
  linkElement: (useCaseId: string, sectionId: string, element: HopexElement) => Promise<boolean>
  unlinkElement: (useCaseId: string, sectionId: string, refId: string) => Promise<boolean>
}

const HopexContext = createContext<HopexContextType | undefined>(undefined)

export function HopexProvider({ children }: { children: React.ReactNode }) {
  const [elements, setElements] = useState<HopexElement[]>([])
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('loading')
  const [isLoading, setIsLoading] = useState(false)

  const fetchElements = useCallback(async () => {
    setIsLoading(true)
    setConnectionStatus('loading')
    try {
      const res = await fetch(ENDPOINTS.hopexCapabilities)
      if (!res.ok) throw new Error('HOPEX unavailable')
      const data = await res.json()
      setElements(data.capabilities || [])
      setConnectionStatus('connected')
    } catch {
      setElements([])
      setConnectionStatus('disconnected')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const searchElements = useCallback(async (query: string, type?: string): Promise<HopexElement[]> => {
    try {
      const params = new URLSearchParams({ q: query })
      if (type) params.set('type', type)
      const res = await fetch(`${ENDPOINTS.hopexSearch}?${params}`)
      if (!res.ok) throw new Error('Search failed')
      const data = await res.json()
      return data.results || []
    } catch {
      return []
    }
  }, [])

  const linkElement = useCallback(async (useCaseId: string, sectionId: string, element: HopexElement): Promise<boolean> => {
    try {
      const res = await fetch(bamReferenceUrl(useCaseId, sectionId), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          toolType: 'HOPEX',
          elementId: element.id,
          elementName: element.name,
          elementType: element.type,
        }),
      })
      return res.ok
    } catch {
      return false
    }
  }, [])

  const unlinkElement = useCallback(async (useCaseId: string, sectionId: string, refId: string): Promise<boolean> => {
    try {
      const res = await fetch(bamReferenceUrl(useCaseId, sectionId, refId), {
        method: 'DELETE',
      })
      return res.ok
    } catch {
      return false
    }
  }, [])

  return (
    <HopexContext.Provider
      value={{
        elements,
        connectionStatus,
        isLoading,
        fetchElements,
        searchElements,
        linkElement,
        unlinkElement,
      }}
    >
      {children}
    </HopexContext.Provider>
  )
}

export function useHopex() {
  const context = useContext(HopexContext)
  if (context === undefined) {
    throw new Error('useHopex must be used within a HopexProvider')
  }
  return context
}
