import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Upload, ArrowRight, Loader2 } from 'lucide-react'
import { fetchDocuments, uploadDocument, type Document } from '../lib/api'

export default function Dashboard() {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments()
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const handleUpload = async (file: File) => {
    setIsUploading(true)
    try {
      const result = await uploadDocument(file)
      await loadDocuments()
      navigate(`/chat?doc=${result.document_id}`)
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') {
      handleUpload(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleUpload(file)
    }
  }

  const uploadedDocs = documents.filter(d => d.source === 'upload')
  const importedDocs = documents.filter(d => d.source === 'bac')

  return (
    <div className="p-8 overflow-auto">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-3xl font-semibold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Upload documents or view imported use cases from BAC</p>
      </div>

      {/* Upload Area */}
      <div
        className={`upload-zone animate-fade-in stagger-1 ${dragOver ? 'dragover' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
            <p className="mt-4 text-muted-foreground">Processing document...</p>
          </div>
        ) : (
          <>
            <Upload className="w-12 h-12 text-muted-foreground/50" />
            <p className="mt-4 text-lg text-muted-foreground">
              Drag and drop a PDF here, or{' '}
              <label className="text-primary hover:underline cursor-pointer">
                browse
                <input
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </label>
            </p>
            <p className="text-sm text-muted-foreground/60 mt-2">PDF files only, max 16MB</p>
          </>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mt-8">
        <div className="card-editorial p-6 animate-fade-in stagger-2">
          <p className="text-sm text-muted-foreground">Total Documents</p>
          <p className="text-3xl font-semibold text-foreground">{documents.length}</p>
        </div>
        <div className="card-editorial p-6 animate-fade-in stagger-3">
          <p className="text-sm text-muted-foreground">Uploaded</p>
          <p className="text-3xl font-semibold text-primary">{uploadedDocs.length}</p>
        </div>
        <div className="card-editorial p-6 animate-fade-in stagger-4">
          <p className="text-sm text-muted-foreground">Imported from BAC</p>
          <p className="text-3xl font-semibold text-emerald-600">{importedDocs.length}</p>
        </div>
      </div>

      {/* Document Lists */}
      {isLoading ? (
        <div className="mt-8 text-center text-muted-foreground">Loading documents...</div>
      ) : (
        <>
          {/* Imported from BAC */}
          {importedDocs.length > 0 && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-foreground mb-4">Imported from BAC</h2>
              <div className="grid grid-cols-2 gap-4">
                {importedDocs.map((doc, idx) => (
                  <div
                    key={doc.id}
                    className={`card-editorial p-4 cursor-pointer animate-fade-in stagger-${Math.min(idx + 1, 5)}`}
                    onClick={() => navigate(`/chat?doc=${doc.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-100 rounded-sm">
                        <FileText className="w-5 h-5 text-emerald-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-foreground truncate">
                          {doc.metadata?.name || doc.filename}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Uploaded Documents */}
          {uploadedDocs.length > 0 && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-foreground mb-4">Uploaded Documents</h2>
              <div className="grid grid-cols-2 gap-4">
                {uploadedDocs.map((doc, idx) => (
                  <div
                    key={doc.id}
                    className={`card-editorial p-4 cursor-pointer animate-fade-in stagger-${Math.min(idx + 1, 5)}`}
                    onClick={() => navigate(`/chat?doc=${doc.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-primary/10 rounded-sm">
                        <FileText className="w-5 h-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-foreground truncate">{doc.filename}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {documents.length === 0 && (
            <div className="mt-8 text-center py-12 text-muted-foreground">
              No documents yet. Upload a PDF or import from BAC.
            </div>
          )}
        </>
      )}
    </div>
  )
}
