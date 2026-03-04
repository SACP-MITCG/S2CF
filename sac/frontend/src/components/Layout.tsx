import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  FileText,
  MessageSquare,
  Database,
  ChevronLeft,
  ChevronRight,
  Layers
} from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const navItems = [
    { path: '/', icon: FileText, label: 'Dashboard' },
    { path: '/chat', icon: MessageSquare, label: 'Architecture Chat' },
    { path: '/models', icon: Database, label: 'Reference Models' },
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
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h1 className="text-base font-serif font-semibold tracking-tight">SAC</h1>
                <p className="text-[10px] text-muted-foreground -mt-0.5">Solution Architecture</p>
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

        {/* Footer */}
        <div className="p-3 border-t border-border">
          <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'justify-center' : ''}`}>
            {!sidebarCollapsed && (
              <p className="text-xs text-muted-foreground animate-fade-in">SACP Unified v0.1.0</p>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {children}
      </main>
    </div>
  )
}
