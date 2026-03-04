import { useEffect, useState, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Send, Loader2, Bot, User, FileText } from 'lucide-react'
import { sendChatMessage, fetchDocument, type Document, type ChatMessage } from '../lib/api'

export default function Chat() {
  const [searchParams] = useSearchParams()
  const docId = searchParams.get('doc')

  const [document, setDocument] = useState<Document | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [showContext, setShowContext] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setSessionId(`session-${Date.now()}`)
  }, [])

  useEffect(() => {
    if (docId) {
      fetchDocument(docId)
        .then(setDocument)
        .catch(console.error)
    }
  }, [docId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const result = await sendChatMessage(userMessage, sessionId, docId || undefined)
      setMessages(prev => [...prev, { role: 'assistant', content: result.response }])
      setSessionId(result.session_id)
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, an error occurred. Please try again.' },
      ])
    } finally {
      setIsLoading(false)
    }
  }, [input, isLoading, sessionId, docId])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border bg-card p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-sm">
            <Bot className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-foreground">Architecture Assistant</h1>
            <p className="text-sm text-muted-foreground">
              {document ? `Context: ${document.filename}` : 'Ask questions about architecture'}
            </p>
          </div>
        </div>
      </div>

      {/* Document Context Banner */}
      {document && (
        <div className="bg-primary/5 border-b border-primary/20 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-primary">
              <FileText className="w-4 h-4" />
              <span className="text-sm font-medium">
                Using context from: {document.metadata?.name || document.filename}
              </span>
            </div>
            <button
              onClick={() => setShowContext(!showContext)}
              className="btn-ghost text-xs"
            >
              {showContext ? 'Hide context' : 'View context'}
            </button>
          </div>
          {showContext && (
            <div className="mt-3 p-3 bg-card rounded-sm border border-border max-h-48 overflow-auto">
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono">
                {document.content}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12 animate-fade-in">
            <Bot className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
            <p className="text-muted-foreground">
              {document
                ? "Ask questions about this document or architecture design."
                : "Upload a document or ask general architecture questions."}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}
          >
            {msg.role === 'assistant' && (
              <div className="p-2 bg-muted rounded-full h-fit">
                <Bot className="w-4 h-4 text-muted-foreground" />
              </div>
            )}
            <div
              className={`max-w-[70%] rounded-sm px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-card border border-border shadow-sm'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
            {msg.role === 'user' && (
              <div className="p-2 bg-primary rounded-full h-fit">
                <User className="w-4 h-4 text-primary-foreground" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="p-2 bg-muted rounded-full h-fit">
              <Bot className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="bg-card border border-border shadow-sm rounded-sm px-4 py-3">
              <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border bg-card p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about architecture, reference models, or your document..."
            className="input-editorial flex-1 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
