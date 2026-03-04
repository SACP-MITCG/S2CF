import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  FileText,
  Clock,
  ArrowRight,
  Sparkles,
  Layout,
  Zap,
  GitBranch,
  RefreshCw
} from 'lucide-react'
import { useUseCases } from '../context/UseCaseContext'
import { useToast } from '../context/ToastContext'
import StatusBadge from '../components/StatusBadge'

const templates = [
  {
    id: 'regulatory_change',
    name: 'Regulatory Change',
    description: 'Compliance-driven requirements',
    icon: GitBranch,
    color: 'text-violet-600 bg-violet-100 dark:bg-violet-900/30'
  },
  {
    id: 'process_improvement',
    name: 'Process Improvement',
    description: 'Optimize existing workflows',
    icon: RefreshCw,
    color: 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30'
  },
  {
    id: 'new_capability',
    name: 'New Capability',
    description: 'Add business capabilities',
    icon: Zap,
    color: 'text-amber-600 bg-amber-100 dark:bg-amber-900/30'
  },
  {
    id: 'integration',
    name: 'System Integration',
    description: 'Connect systems together',
    icon: Layout,
    color: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30'
  },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { useCases, fetchUseCases, createUseCase, isLoading } = useUseCases()
  const { addToast } = useToast()
  const [showTemplates, setShowTemplates] = useState(false)

  useEffect(() => {
    fetchUseCases()
  }, [fetchUseCases])

  const handleCreateUseCase = async (templateId?: string) => {
    try {
      const id = await createUseCase('New Use Case', templateId)
      addToast('Use case created', 'success')
      navigate(`/usecase/${id}`)
    } catch {
      addToast('Failed to create use case', 'error')
    }
    setShowTemplates(false)
  }

  return (
    <div className="flex-1 overflow-auto">
      {/* Header */}
      <header className="sticky top-0 z-10 flex items-center justify-between h-[var(--header-height)] px-8 border-b border-border bg-background/80 backdrop-blur-sm">
        <div>
          <h1 className="text-2xl font-serif">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Manage your business use cases</p>
        </div>
        <div className="relative">
          <button
            onClick={() => setShowTemplates(!showTemplates)}
            className="btn-primary"
          >
            <Plus className="w-4 h-4" />
            New Use Case
          </button>

          {/* Template Dropdown */}
          {showTemplates && (
            <div className="absolute right-0 top-full mt-2 w-80 p-2 rounded-sm border border-border bg-card shadow-lg animate-fade-in z-20">
              <p className="px-3 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Select Template
              </p>
              {templates.map((template) => {
                const Icon = template.icon
                return (
                  <button
                    key={template.id}
                    onClick={() => handleCreateUseCase(template.id)}
                    className="flex items-start gap-3 w-full p-3 rounded-sm text-left hover:bg-muted transition-colors"
                  >
                    <div className={`flex items-center justify-center w-9 h-9 rounded-sm ${template.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{template.name}</p>
                      <p className="text-xs text-muted-foreground">{template.description}</p>
                    </div>
                  </button>
                )
              })}
              <div className="divider-editorial my-2" />
              <button
                onClick={() => handleCreateUseCase('blank')}
                className="flex items-center gap-3 w-full p-3 rounded-sm text-left hover:bg-muted transition-colors"
              >
                <div className="flex items-center justify-center w-9 h-9 rounded-sm bg-muted">
                  <FileText className="w-4 h-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-sm font-medium">Blank Template</p>
                  <p className="text-xs text-muted-foreground">Start from scratch</p>
                </div>
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="p-8">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Use Cases', value: useCases.length, icon: FileText },
            { label: 'In Progress', value: useCases.filter(u => u.status === 'draft').length, icon: Clock },
            { label: 'In Review', value: useCases.filter(u => u.status === 'in_review').length, icon: RefreshCw },
            { label: 'Approved', value: useCases.filter(u => u.status === 'approved').length, icon: Sparkles },
          ].map((stat, index) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.label}
                className={`card-editorial p-5 animate-fade-in stagger-${index + 1}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <Icon className="w-5 h-5 text-muted-foreground" />
                </div>
                <p className="text-3xl font-serif font-semibold">{stat.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              </div>
            )
          })}
        </div>

        {/* Use Cases List */}
        <div className="mb-6">
          <h2 className="text-lg font-serif mb-4">Recent Use Cases</h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-48 text-muted-foreground">
            <RefreshCw className="w-5 h-5 animate-spin mr-2" />
            Loading...
          </div>
        ) : useCases.length === 0 ? (
          <div className="card-editorial p-12 text-center animate-fade-in">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-muted">
              <FileText className="w-6 h-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-serif mb-2">No use cases yet</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Create your first use case to get started with business analysis.
            </p>
            <button onClick={() => setShowTemplates(true)} className="btn-primary">
              <Plus className="w-4 h-4" />
              Create Use Case
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {useCases.map((useCase, index) => (
              <button
                key={useCase.id}
                onClick={() => navigate(`/usecase/${useCase.id}`)}
                className={`card-editorial p-5 text-left group animate-fade-in stagger-${(index % 5) + 1}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center justify-center w-10 h-10 rounded-sm bg-primary/10">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <StatusBadge status={useCase.status} showDot />
                </div>

                <h3 className="text-base font-serif font-medium mb-1 group-hover:text-primary transition-colors">
                  {useCase.title}
                </h3>

                <div className="flex items-center gap-4 text-xs text-muted-foreground mt-3">
                  <span className="flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    {useCase.sectionCount} sections
                  </span>
                  {useCase.createdAt && (
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(useCase.createdAt).toLocaleDateString()}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1 mt-4 text-xs text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                  Open <ArrowRight className="w-3 h-3" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Click outside to close dropdown */}
      {showTemplates && (
        <div
          className="fixed inset-0"
          onClick={() => setShowTemplates(false)}
        />
      )}
    </div>
  )
}
