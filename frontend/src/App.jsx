import { useState, useEffect, useRef, useCallback } from 'react'
import Header from './components/Header.jsx'
import Sidebar from './components/Sidebar.jsx'
import ChatMessage from './components/ChatMessage.jsx'
import QueryInput from './components/QueryInput.jsx'
import MandalaBackground from './components/MandalaBackground.jsx'
import { getWisdom, getHealth } from './services/api.js'

const WELCOME_QUERIES = [
  "I feel lost and don't know my purpose",
  "How do I deal with failure at work?",
  "I'm struggling with anger and resentment",
  "How can I find inner peace?",
  "What does the Gita say about detachment?",
  "I'm afraid of making important decisions",
]

function WelcomeScreen({ onQuery }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-6xl mb-5 animate-float select-none">🕉️</div>

      <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-saffron via-gold to-saffron bg-clip-text text-transparent">
        Seek Wisdom
      </h2>
      <p className="text-cream-dark text-base mb-2 max-w-md leading-relaxed">
        Ask anything about life's challenges and receive guidance rooted in the eternal teachings of the Bhagavad Gita.
      </p>
      <p className="text-text-muted text-xs mb-10">
        Type below or choose a question to begin
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
        {WELCOME_QUERIES.map((q, i) => (
          <button
            key={i}
            onClick={() => onQuery(q)}
            className="text-left p-4 card hover:border-saffron/40 hover:bg-midnight-200
                       transition-all duration-200 text-cream-dark hover:text-cream text-sm group"
          >
            <span className="text-saffron mr-2 group-hover:text-gold transition-colors">✦</span>
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 msg-enter">
      <div className="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center text-base
                      bg-gradient-to-br from-saffron to-gold shadow-saffron">
        🕉️
      </div>
      <div className="card rounded-2xl rounded-tl-none px-5 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xs text-text-muted">Reflecting on wisdom</span>
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-saffron dot-1" />
            <div className="w-2 h-2 rounded-full bg-saffron dot-2" />
            <div className="w-2 h-2 rounded-full bg-saffron dot-3" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [apiStatus, setApiStatus] = useState(null)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  // Health check on mount
  useEffect(() => {
    getHealth()
      .then(setApiStatus)
      .catch(() => setApiStatus(null))
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleQuery = useCallback(
    async (query) => {
      if (!query.trim() || isLoading) return

      const userMsg = { role: 'user', content: query, timestamp: new Date() }
      setMessages((prev) => [...prev, userMsg])
      setIsLoading(true)
      setError(null)

      try {
        const data = await getWisdom(query, sessionId)
        setSessionId(data.session_id)

        const assistantMsg = {
          role: 'assistant',
          content: data.response,
          verses: data.used_verses || [],
          themes: data.themes || [],
          timestamp: new Date(),
          error: data.error,
        }
        setMessages((prev) => [...prev, assistantMsg])
      } catch (err) {
        setError(err.message || 'Failed to reach the wisdom service. Is the backend running?')
        // Remove the user message that errored out so they can retry
        setMessages((prev) => prev.slice(0, -1))
      } finally {
        setIsLoading(false)
      }
    },
    [isLoading, sessionId]
  )

  const handleClear = useCallback(() => {
    setMessages([])
    setSessionId(null)
    setError(null)
  }, [])

  return (
    <div className="min-h-screen bg-midnight flex flex-col relative overflow-hidden">
      <MandalaBackground />

      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSampleQuery={(q) => { setSidebarOpen(false); handleQuery(q) }}
        apiStatus={apiStatus}
        messageCount={messages.length}
      />

      {/* Main layout — full viewport height */}
      <div className="relative z-10 flex flex-col h-screen">
        <Header
          onMenuClick={() => setSidebarOpen((o) => !o)}
          apiStatus={apiStatus}
          messages={messages}
          onNewChat={handleClear}
        />

        {/* Scrollable messages area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
            {messages.length === 0 && !isLoading && (
              <WelcomeScreen onQuery={handleQuery} />
            )}

            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}

            {isLoading && <TypingIndicator />}

            {error && (
              <div className="card border-red-500/30 bg-red-900/10 p-4 text-red-300 text-sm flex items-start gap-2">
                <span>⚠</span>
                <span>{error}</span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </main>

        {/* Fixed input bar */}
        <div className="flex-shrink-0 border-t border-midnight-300 bg-midnight/90 backdrop-blur-xl">
          <div className="max-w-3xl mx-auto px-4 py-4">
            <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
            <p className="text-center text-[10px] text-text-muted mt-2">
              Shift+Enter for new line · guidance is spiritual, not medical advice
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
