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
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Upload documents or view imported use cases from BAC</p>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
            <p className="mt-4 text-gray-600">Processing document...</p>
          </div>
        ) : (
          <>
            <Upload className="w-12 h-12 text-gray-400 mx-auto" />
            <p className="mt-4 text-lg text-gray-600">
              Drag and drop a PDF here, or{' '}
              <label className="text-blue-600 hover:underline cursor-pointer">
                browse
                <input
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </label>
            </p>
            <p className="text-sm text-gray-400 mt-2">PDF files only, max 16MB</p>
          </>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mt-8">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Total Documents</p>
          <p className="text-3xl font-bold text-gray-900">{documents.length}</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Uploaded</p>
          <p className="text-3xl font-bold text-blue-600">{uploadedDocs.length}</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <p className="text-sm text-gray-500">Imported from BAC</p>
          <p className="text-3xl font-bold text-green-600">{importedDocs.length}</p>
        </div>
      </div>

      {/* Document Lists */}
      {isLoading ? (
        <div className="mt-8 text-center text-gray-500">Loading documents...</div>
      ) : (
        <>
          {/* Imported from BAC */}
          {importedDocs.length > 0 && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Imported from BAC</h2>
              <div className="grid grid-cols-2 gap-4">
                {importedDocs.map(doc => (
                  <div
                    key={doc.id}
                    className="bg-white rounded-lg p-4 shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/chat?doc=${doc.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <FileText className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {doc.metadata?.name || doc.filename}
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Uploaded Documents */}
          {uploadedDocs.length > 0 && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Uploaded Documents</h2>
              <div className="grid grid-cols-2 gap-4">
                {uploadedDocs.map(doc => (
                  <div
                    key={doc.id}
                    className="bg-white rounded-lg p-4 shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/chat?doc=${doc.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{doc.filename}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {documents.length === 0 && (
            <div className="mt-8 text-center py-12 text-gray-500">
              No documents yet. Upload a PDF or import from BAC.
            </div>
          )}
        </>
      )}
    </div>
  )
}
