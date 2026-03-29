import { Building2, ExternalLink, Link2, X } from 'lucide-react'
import type { SectionUI, BAMReferenceUI } from '../types/irm'

interface SectionEditorProps {
  section: SectionUI
  editingContent: string
  onContentChange: (content: string) => void
  onTitleChange: (title: string) => void
  onSave: () => void
  onUnlinkBAMReference?: (refId: string) => void
}

export default function SectionEditor({
  section,
  editingContent,
  onContentChange,
  onTitleChange,
  onSave,
  onUnlinkBAMReference,
}: SectionEditorProps) {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <input
        type="text"
        value={section.title}
        onChange={(e) => onTitleChange(e.target.value)}
        className="w-full text-2xl font-serif font-semibold bg-transparent border-none outline-none mb-6 placeholder:text-muted-foreground/50"
        placeholder="Section title..."
      />

      {/* BAM References */}
      {section.bamReferences.length > 0 && (
        <BAMReferencesDisplay
          references={section.bamReferences}
          onUnlink={onUnlinkBAMReference}
        />
      )}

      <textarea
        value={editingContent}
        onChange={(e) => onContentChange(e.target.value)}
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === 's') {
            e.preventDefault()
            onSave()
          }
        }}
        className="w-full min-h-[400px] p-4 rounded-sm border border-border bg-card resize-none outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-mono text-sm leading-relaxed"
        placeholder="Write your content here using Markdown..."
      />

      <p className="text-xs text-muted-foreground mt-4">
        Tip: Use Markdown for formatting. Press Cmd/Ctrl + S to save.
      </p>
    </div>
  )
}

function BAMReferencesDisplay({
  references,
  onUnlink,
}: {
  references: BAMReferenceUI[]
  onUnlink?: (refId: string) => void
}) {
  return (
    <div className="mb-6 p-4 rounded-sm bg-primary/5 border border-primary/20">
      <p className="text-xs font-medium text-primary mb-3 flex items-center gap-1">
        <Link2 className="w-3 h-3" />
        Linked Architecture Elements
      </p>
      <div className="flex flex-wrap gap-2">
        {references.map((ref) => (
          <span
            key={ref.id}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs bg-card rounded-sm border border-border group"
          >
            <Building2 className="w-3 h-3 text-muted-foreground" />
            {ref.elementName}
            {ref.deepLink ? (
              <a
                href={ref.deepLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary"
              >
                <ExternalLink className="w-3 h-3" />
              </a>
            ) : (
              <ExternalLink className="w-3 h-3 text-muted-foreground" />
            )}
            {onUnlink && (
              <button
                onClick={() => onUnlink(ref.id)}
                className="text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </span>
        ))}
      </div>
    </div>
  )
}
