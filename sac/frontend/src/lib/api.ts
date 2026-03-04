const API_BASE = '/api'

export interface Document {
  id: string
  filename: string
  content: string
  recommendation?: string
  metadata?: { name?: string; [key: string]: unknown }
  source: string
  irm_id?: string
  created_at: string
}

export interface ReferenceModel {
  id: string
  name: string
  description: string
  tags: string[]
  score?: number
  addedAt: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// Documents API
export async function fetchDocuments(source?: string): Promise<Document[]> {
  const url = source ? `${API_BASE}/documents?source=${source}` : `${API_BASE}/documents`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch documents')
  return res.json()
}

export async function fetchDocument(id: string): Promise<Document> {
  const res = await fetch(`${API_BASE}/documents/${id}`)
  if (!res.ok) throw new Error('Failed to fetch document')
  return res.json()
}

export async function uploadDocument(file: File): Promise<{ document_id: string; recommendation: string }> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Failed to upload document')
  return res.json()
}

// Chat API
export async function sendChatMessage(
  message: string,
  sessionId?: string,
  documentId?: string
): Promise<{ response: string; session_id: string }> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, document_id: documentId }),
  })
  if (!res.ok) throw new Error('Failed to send message')
  return res.json()
}

export async function fetchChatHistory(sessionId: string): Promise<{ history: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/chat/history/${sessionId}`)
  if (!res.ok) throw new Error('Failed to fetch history')
  return res.json()
}

// Reference Models API
export async function fetchModels(): Promise<ReferenceModel[]> {
  const res = await fetch(`${API_BASE}/models`)
  if (!res.ok) throw new Error('Failed to fetch models')
  return res.json()
}

export async function addModel(name: string, description: string, tags: string[]): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE}/models`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description, tags }),
  })
  if (!res.ok) throw new Error('Failed to add model')
  return res.json()
}

export async function searchModels(query: string, topK = 5): Promise<{ results: ReferenceModel[] }> {
  const res = await fetch(`${API_BASE}/models/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  })
  if (!res.ok) throw new Error('Failed to search models')
  return res.json()
}

// IRM Documents API
export async function fetchIRMDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/irm/documents`)
  if (!res.ok) throw new Error('Failed to fetch IRM documents')
  return res.json()
}
