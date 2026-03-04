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
    // Generate session ID
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
      <div className="border-b bg-white p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Bot className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Architecture Assistant</h1>
            <p className="text-sm text-gray-500">
              {document ? `Context: ${document.filename}` : 'Ask questions about architecture'}
            </p>
          </div>
        </div>
      </div>

      {/* Document Context Banner */}
      {document && (
        <div className="bg-blue-50 border-b border-blue-100 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-700">
              <FileText className="w-4 h-4" />
              <span className="text-sm font-medium">
                Using context from: {document.metadata?.name || document.filename}
              </span>
            </div>
            <button
              onClick={() => setShowContext(!showContext)}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
            >
              {showContext ? 'Hide context' : 'View context'}
            </button>
          </div>
          {showContext && (
            <div className="mt-3 p-3 bg-white rounded border border-blue-200 max-h-48 overflow-auto">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {document.content}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">
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
              <div className="p-2 bg-gray-100 rounded-full h-fit">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
            )}
            <div
              className={`max-w-[70%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border shadow-sm'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
            {msg.role === 'user' && (
              <div className="p-2 bg-blue-600 rounded-full h-fit">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="p-2 bg-gray-100 rounded-full h-fit">
              <Bot className="w-4 h-4 text-gray-600" />
            </div>
            <div className="bg-white border shadow-sm rounded-lg px-4 py-3">
              <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about architecture, reference models, or your document..."
            className="flex-1 border rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
