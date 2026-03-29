// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// SAC (Solution Architecture Co-Pilot) URL - points to new sacp-unified on port 5002
export const SAC_BASE_URL = import.meta.env.VITE_SAC_URL || 'http://localhost:5002'

// API endpoints
export const ENDPOINTS = {
  usecases: `${API_BASE_URL}/usecases`,
  upload: `${API_BASE_URL}/upload`,
  hopex: `${API_BASE_URL}/hopex`,
  hopexHealth: `${API_BASE_URL}/hopex/health`,
  hopexCapabilities: `${API_BASE_URL}/hopex/capabilities`,
  hopexProcesses: `${API_BASE_URL}/hopex/processes`,
  hopexApplications: `${API_BASE_URL}/hopex/applications`,
  hopexSearch: `${API_BASE_URL}/hopex/search`,
  export: `${API_BASE_URL}/export`,
  // SAC integration
  sacIrmImport: `${SAC_BASE_URL}/api/irm/import`,
}

/** Build BAM reference endpoints for a given use case + section */
export function bamReferenceUrl(useCaseId: string, sectionId: string, refId?: string) {
  const base = `${ENDPOINTS.usecases}/${useCaseId}/sections/${sectionId}/bam-references`
  return refId ? `${base}/${refId}` : base
}
