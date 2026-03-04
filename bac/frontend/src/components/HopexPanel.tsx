import { useState, useEffect } from 'react'
import { Building2, CheckCircle2, Link2, Search, X } from 'lucide-react'
import type { HopexElement } from '../types/irm'
import { useHopex } from '../context/HopexContext'

interface HopexPanelProps {
  visible: boolean
  onClose: () => void
  /** Called when user clicks "link" on an element. Receives the element to link to the active section. */
  onLinkElement?: (element: HopexElement) => void
}

export default function HopexPanel({ visible, onClose, onLinkElement }: HopexPanelProps) {
  const { elements, connectionStatus, isLoading, fetchElements } = useHopex()
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (visible) {
      fetchElements()
    }
  }, [visible, fetchElements])

  if (!visible) return null

  const filtered = elements.filter(
    (el) =>
      el.name.toLowerCase().includes(search.toLowerCase()) ||
      el.description?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <aside className="w-[var(--panel-width)] flex-shrink-0 border-l border-border bg-card/50 flex flex-col animate-panel-slide">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-medium">HOPEX Browser</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-sm hover:bg-muted text-muted-foreground hover:text-foreground"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search elements..."
            className="input-editorial pl-9"
          />
        </div>
      </div>

      <div className="flex-1 overflow-auto p-3 space-y-2">
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            Loading elements...
          </div>
        ) : (
          filtered.map((element, index) => (
            <div
              key={element.id}
              className={`hopex-element animate-fade-in stagger-${(index % 5) + 1}`}
            >
              <div className="flex items-center justify-center w-8 h-8 rounded-sm bg-muted flex-shrink-0">
                <Building2 className="w-4 h-4 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{element.name}</p>
                <p className="text-[10px] text-muted-foreground truncate">{element.type}</p>
              </div>
              <button
                onClick={() => onLinkElement?.(element)}
                className="p-1.5 rounded-sm hover:bg-primary/10 text-muted-foreground hover:text-primary transition-colors"
                title={onLinkElement ? 'Link to active section' : 'Select a section first'}
              >
                <Link2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}

        {!isLoading && filtered.length === 0 && (
          <div className="text-center py-8 text-muted-foreground text-sm">
            {connectionStatus === 'disconnected'
              ? 'HOPEX not available'
              : 'No elements found'}
          </div>
        )}
      </div>

      <div className="p-3 border-t border-border text-center">
        <p className="text-[10px] text-muted-foreground">
          {connectionStatus === 'connected' ? (
            <>
              <CheckCircle2 className="w-3 h-3 inline mr-1 text-emerald-500" />
              Connected to HOPEX
            </>
          ) : connectionStatus === 'disconnected' ? (
            <>
              <X className="w-3 h-3 inline mr-1 text-destructive" />
              HOPEX unavailable — using mock data
            </>
          ) : (
            'Connecting...'
          )}
        </p>
      </div>
    </aside>
  )
}
