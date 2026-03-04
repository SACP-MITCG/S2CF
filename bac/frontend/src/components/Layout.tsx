import { useState, useCallback } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Upload,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Building2
} from 'lucide-react'
import { useUseCases } from '../context/UseCaseContext'
import { useToast } from '../context/ToastContext'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const { uploadDocument, suggestTemplate } = useUseCases()
  const { addToast } = useToast()

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length === 0) return

    const file = files[0]
    addToast(`Uploading ${file.name}...`, 'info')

    try {
      const result = await uploadDocument(file)
      const suggestion = await suggestTemplate(result.documentId)
      addToast(`Recommended template: ${suggestion.suggestedTemplate}`, 'success')
    } catch {
      addToast('Upload failed', 'error')
    }
  }, [uploadDocument, suggestTemplate, addToast])

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/usecases', icon: FileText, label: 'Use Cases' },
  ]

  return (
    <div className="flex h-screen bg-background paper-texture">
      {/* Sidebar */}
      <aside
        className={`
          flex flex-col h-full border-r border-border bg-card/50 backdrop-blur-sm
          transition-all duration-300 ease-out
          ${sidebarCollapsed ? 'w-16' : 'w-[var(--sidebar-width)]'}
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-[var(--header-height)] px-4 border-b border-border">
          {!sidebarCollapsed && (
            <Link to="/" className="flex items-center gap-2.5 animate-fade-in">
              <div className="flex items-center justify-center w-8 h-8 rounded-sm bg-primary text-primary-foreground">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h1 className="text-base font-serif font-semibold tracking-tight">BAC</h1>
                <p className="text-[10px] text-muted-foreground -mt-0.5">Business Analysis</p>
              </div>
            </Link>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-1.5 rounded-sm hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item, index) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item animate-slide-in-left stagger-${index + 1} ${isActive ? 'active' : ''}`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Upload Zone */}
        {!sidebarCollapsed && (
          <div className="p-3 animate-fade-in stagger-3">
            <div
              className={`upload-zone ${isDragging ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Upload className="w-5 h-5" />
              <span className="text-center">
                Drop document here
                <br />
                <span className="text-xs text-muted-foreground/70">PDF, Word, Excel</span>
              </span>
            </div>
          </div>
        )}

        {/* HOPEX Connection Status */}
        <div className="p-3 border-t border-border">
          <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'justify-center' : ''}`}>
            <div className="flex items-center justify-center w-8 h-8 rounded-sm bg-muted">
              <Building2 className="w-4 h-4 text-muted-foreground" />
            </div>
            {!sidebarCollapsed && (
              <div className="animate-fade-in">
                <p className="text-xs font-medium">HOPEX</p>
                <p className="text-[10px] text-emerald-600">Connected</p>
              </div>
            )}
          </div>
        </div>

        {/* Settings */}
        <div className="p-3 border-t border-border">
          <button className={`nav-item w-full ${sidebarCollapsed ? 'justify-center px-0' : ''}`}>
            <Settings className="w-4 h-4 flex-shrink-0" />
            {!sidebarCollapsed && <span>Settings</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {children}
      </main>
    </div>
  )
}
