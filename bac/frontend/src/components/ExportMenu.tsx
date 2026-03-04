import { useState, useCallback } from 'react'
import { Download, FileText, Loader2, Send, Sparkles } from 'lucide-react'
import { ENDPOINTS, SAC_BASE_URL } from '../config'
import { useToast } from '../context/ToastContext'

interface ExportMenuProps {
  useCaseId: string
  useCaseTitle: string
}

export default function ExportMenu({ useCaseId, useCaseTitle }: ExportMenuProps) {
  const [showMenu, setShowMenu] = useState(false)
  const [isSendingToSAC, setIsSendingToSAC] = useState(false)
  const { addToast } = useToast()

  const handleExport = useCallback(
    async (format: 'markdown' | 'irm' | 'word') => {
      setShowMenu(false)

      try {
        const res = await fetch(`${ENDPOINTS.export}/${format}/${useCaseId}`)
        if (!res.ok) throw new Error('Export failed')

        if (format === 'irm') {
          const data = await res.json()
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${useCaseTitle || 'usecase'}.json`
          a.click()
          URL.revokeObjectURL(url)
        } else {
          const blob = await res.blob()
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${useCaseTitle || 'usecase'}.${format === 'markdown' ? 'md' : 'docx'}`
          a.click()
          URL.revokeObjectURL(url)
        }

        addToast(`Exported as ${format.toUpperCase()}`, 'success')
      } catch {
        addToast('Export failed', 'error')
      }
    },
    [useCaseId, useCaseTitle, addToast]
  )

  const handleSendToSAC = useCallback(async () => {
    setIsSendingToSAC(true)

    try {
      const exportRes = await fetch(`${ENDPOINTS.export}/irm/${useCaseId}`)
      if (!exportRes.ok) throw new Error('Failed to export IRM')

      const irmData = await exportRes.json()

      const sacRes = await fetch(ENDPOINTS.sacIrmImport, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(irmData),
      })

      if (!sacRes.ok) {
        const errorData = await sacRes.json().catch(() => ({}))
        throw new Error(errorData.error || 'Failed to send to SAC')
      }

      const result = await sacRes.json()
      addToast(`Sent to SAC successfully! Document ID: ${result.document_id}`, 'success')
      window.open(`${SAC_BASE_URL}?doc=${result.document_id}`, '_blank')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to send to SAC'
      addToast(message, 'error')
    } finally {
      setIsSendingToSAC(false)
    }
  }, [useCaseId, addToast])

  return (
    <>
      <div className="relative">
        <button onClick={() => setShowMenu(!showMenu)} className="btn-secondary">
          <Download className="w-4 h-4" />
          Export
        </button>

        {showMenu && (
          <div className="absolute right-0 top-full mt-2 w-48 p-1 rounded-sm border border-border bg-card shadow-lg z-20 animate-fade-in">
            <button
              onClick={() => handleExport('markdown')}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left rounded-sm hover:bg-muted"
            >
              <FileText className="w-4 h-4" />
              Markdown
            </button>
            <button
              onClick={() => handleExport('word')}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left rounded-sm hover:bg-muted"
            >
              <FileText className="w-4 h-4" />
              Word Document
            </button>
            <button
              onClick={() => handleExport('irm')}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left rounded-sm hover:bg-muted"
            >
              <Sparkles className="w-4 h-4" />
              IRM JSON-LD
            </button>
          </div>
        )}
      </div>

      <button
        onClick={handleSendToSAC}
        disabled={isSendingToSAC}
        className="btn-primary"
        title="Send to Solution Architecture Co-Pilot"
      >
        {isSendingToSAC ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
        Send to SAC
      </button>

      {/* Click outside to close export menu */}
      {showMenu && <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />}
    </>
  )
}
