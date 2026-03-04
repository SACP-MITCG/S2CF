// IRM (Intermediate Representation Model) TypeScript types
// Aligned with backend app/models/irm.py

export type SectionType =
  | 'Overview'
  | 'BusinessContext'
  | 'SMARTObjective'
  | 'UserJourney'
  | 'Assumptions'
  | 'OpenQuestions'
  | 'BAMReferences'
  | 'ValidationStatus'
  | 'CustomSection'

export type SectionStatus = 'draft' | 'in_review' | 'approved' | 'rejected'

export interface IRMMeta {
  'sacp:createdBy': string
  'sacp:createdAt': string | null
  'sacp:version': string
  'sacp:sourceDocument': string | null
  'sacp:sourceSection': string | null
  'sacp:validationStatus': SectionStatus
  'sacp:confidence': number | null
  'sacp:lastValidatedBy': string | null
  'sacp:lastValidatedAt': string | null
}

export interface BAMReference {
  '@type': 'sacp:BAMReference'
  '@id': string
  'sacp:toolType': 'HOPEX' | 'Signavio'
  'sacp:elementId': string
  'sacp:elementType': string
  'sacp:elementName': string
  'sacp:diagramId': string | null
  'sacp:embedUrl': string | null
  'sacp:deepLink': string | null
}

export interface Section {
  '@type': string
  '@id': string
  'sacp:title': string
  'sacp:content': string
  'sacp:order': number
  'sacp:bamReferences': BAMReference[]
  'sacp:meta': IRMMeta
}

export interface UseCaseDescription {
  '@context': string
  '@type': 'sacp:UseCaseDescription'
  '@id': string
  'sacp:title': string
  'sacp:description': string
  'sacp:templateId': string | null
  'sacp:sections': Section[]
  'sacp:meta': IRMMeta
}

// Simplified types for UI state management
export interface UseCaseSummary {
  id: string
  title: string
  sectionCount: number
  status: SectionStatus
  createdAt: string | null
}

export interface SectionUI {
  id: string
  type: SectionType
  title: string
  content: string
  order: number
  status: SectionStatus
  bamReferences: BAMReferenceUI[]
}

export interface BAMReferenceUI {
  id: string
  toolType: 'HOPEX' | 'Signavio'
  elementId: string
  elementType: string
  elementName: string
  diagramId?: string
  embedUrl?: string
  deepLink?: string
}

export interface UseCaseUI {
  id: string
  title: string
  description: string
  templateId: string | null
  sections: SectionUI[]
  status: SectionStatus
  createdAt: string | null
}

// Template types
export interface Template {
  id: string
  name: string
  description: string
  sectionCount: number
}

// HOPEX element types
export interface HopexElement {
  id: string
  name: string
  description: string
  type: 'BusinessCapability' | 'BusinessProcess' | 'Application'
  level?: number
  parent?: { id: string; name: string }
}

export interface HopexDiagram {
  id: string
  name: string
  type: string
  lastModified?: string
}

// Document extraction types
export interface DocumentExtraction {
  filename: string
  extension: string
  text: string
  images: Array<{
    page: number
    index: number
    width: number
    height: number
    format: string
    base64: string
  }>
  metadata: Record<string, unknown>
  error?: string
}

export interface TemplateSuggestion {
  suggestedTemplate: string
  confidence: number
  reasoning: string
  alternatives: string[]
}
