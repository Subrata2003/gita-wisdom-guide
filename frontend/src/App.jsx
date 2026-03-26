import { useState, useEffect, useRef, useCallback } from 'react'
import Header from './components/Header.jsx'
import Sidebar from './components/Sidebar.jsx'
import ChatMessage from './components/ChatMessage.jsx'
import QueryInput from './components/QueryInput.jsx'
import MandalaBackground from './components/MandalaBackground.jsx'
import DailyVerse from './components/DailyVerse.jsx'
import JournalPage from './components/JournalPage.jsx'
import ChapterExplorer from './components/ChapterExplorer.jsx'
import ChapterDetail from './components/ChapterDetail.jsx'
import { streamWisdom, getHealth } from './services/api.js'
import { useJournal } from './hooks/useJournal.js'

const WELCOME_QUERIES = [
  "I feel lost and don't know my purpose",
  "How do I deal with failure at work?",
  "I'm struggling with anger and resentment",
  "How can I find inner peace?",
  "What does the Gita say about detachment?",
  "I'm afraid of making important decisions",
]

function WelcomeScreen({ onQuery, onSaveReflection }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 px-4 text-center">
      {/* Hero Om image — screen blend mode removes dark background, gold Om glows through */}
      <div
        className="animate-float mb-3 select-none"
        style={{ width: 192, height: 192, background: 'transparent' }}
      >
        <img
          src="/images/hero-om-V2.png"
          alt="Om symbol"
          width={192}
          height={192}
          className="w-full h-full object-contain"
        />
      </div>

      <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-saffron via-gold to-saffron bg-clip-text text-transparent">
        Seek Wisdom
      </h2>
      <p className="text-cream-dark text-base mb-2 max-w-md leading-relaxed">
        Ask anything about life's challenges and receive guidance rooted in the eternal teachings of the Bhagavad Gita.
      </p>
      <p className="text-text-muted text-xs mb-10">
        Type below or choose a question to begin
      </p>

      {/* Daily Verse */}
      <DailyVerse onQuery={onQuery} onSaveReflection={onSaveReflection} />

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
      <div className="w-9 h-9 flex-shrink-0 flex items-center justify-center">
        <img
          src="/images/chat_app_logo.png"
          alt="Krishna"
          className="w-full h-full object-contain"
        />
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
  const [messages, setMessages]     = useState([])
  const [isLoading, setIsLoading]   = useState(false)
  const [sessionId, setSessionId]   = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [apiStatus, setApiStatus]   = useState(null)
  const [error, setError]           = useState(null)
  const [view, setView]             = useState('chat')   // 'chat' | 'journal' | 'explorer' | 'chapter'
  const [activeChapter, setActiveChapter] = useState(null)
  const { entries, addEntry, deleteEntry, total: journalCount } = useJournal()
  const bottomRef = useRef(null)

  const handleSaveReflection = useCallback((text, source) => {
    addEntry(text, source)
  }, [addEntry])

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
    (query) => {
      if (!query.trim() || isLoading) return

      const userMsg = { role: 'user', content: query, timestamp: new Date() }

      // Placeholder streaming message — content fills in token by token
      const streamingMsg = {
        role: 'assistant',
        content: '',
        streaming: true,
        verses: [],
        themes: [],
        timestamp: new Date(),
        error: false,
      }

      setMessages((prev) => [...prev, userMsg, streamingMsg])
      setIsLoading(true)
      setError(null)

      streamWisdom(query, sessionId, {
        onToken: (token) => {
          setMessages((prev) => {
            const msgs = [...prev]
            const last = msgs[msgs.length - 1]
            if (last?.streaming) {
              msgs[msgs.length - 1] = { ...last, content: last.content + token }
            }
            return msgs
          })
        },

        onDone: (event) => {
          setSessionId(event.session_id)
          setMessages((prev) => {
            const msgs = [...prev]
            const last = msgs[msgs.length - 1]
            if (last?.streaming) {
              msgs[msgs.length - 1] = {
                ...last,
                streaming: false,
                verses: event.verses  || [],
                themes: event.themes  || [],
              }
            }
            return msgs
          })
          setIsLoading(false)
        },

        onError: (err) => {
          setError(err.message || 'Failed to reach the wisdom service. Is the backend running?')
          setMessages((prev) => prev.filter((m) => !m.streaming).slice(0, -1))
          setIsLoading(false)
        },
      })
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
      {/* Full-page atmospheric background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <img
          src="/images/bg-temple.png"
          alt=""
          aria-hidden="true"
          className="w-full h-full object-cover"
          style={{ opacity: 0.20 }}
        />
        {/* Dark overlay to keep UI readable */}
        <div className="absolute inset-0" style={{ background: 'rgba(10, 13, 46, 0.72)' }} />
      </div>
      <MandalaBackground />

      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSampleQuery={(q) => { setSidebarOpen(false); setView('chat'); handleQuery(q) }}
        onOpenJournal={() => setView('journal')}
        onOpenExplorer={() => setView('explorer')}
        apiStatus={apiStatus}
        messageCount={messages.length}
        journalCount={journalCount}
      />

      {/* Main layout — full viewport height */}
      <div className="relative z-10 flex flex-col h-screen">
        <Header
          onMenuClick={() => setSidebarOpen((o) => !o)}
          apiStatus={apiStatus}
          messages={messages}
          onNewChat={handleClear}
        />

        {/* Scrollable messages area — input is sticky inside this, flows with content */}
        <main className="flex-1 overflow-y-auto flex flex-col">

          {/* Journal view */}
          {view === 'journal' && (
            <div className="flex-1">
              <div className="max-w-2xl mx-auto px-4 pt-4">
                <button onClick={() => setView('chat')}
                  className="text-[12px] text-text-muted hover:text-cream transition-colors mb-2 flex items-center gap-1">
                  ← Back to conversation
                </button>
              </div>
              <JournalPage entries={entries} onDelete={deleteEntry} />
            </div>
          )}

          {/* Chapter Explorer */}
          {view === 'explorer' && (
            <div className="flex-1">
              <ChapterExplorer
                onSelectChapter={(ch) => { setActiveChapter(ch); setView('chapter') }}
              />
            </div>
          )}

          {/* Chapter Detail */}
          {view === 'chapter' && activeChapter && (
            <div className="flex-1">
              <ChapterDetail
                chapter={activeChapter}
                onBack={() => setView('explorer')}
                onAskKrishna={(verse) => {
                  setView('chat')
                  handleQuery(`Explain the deep meaning of Chapter ${verse.chapter}, Verse ${verse.verse} and how I can apply it in my life`)
                }}
                onSaveReflection={handleSaveReflection}
              />
            </div>
          )}

          {view === 'chat' && (
          <div className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 space-y-5">
            {messages.length === 0 && !isLoading && (
              <WelcomeScreen onQuery={handleQuery} onSaveReflection={handleSaveReflection} />
            )}

            {messages.map((msg, idx) => (
              <ChatMessage
                key={idx}
                message={msg}
                onSaveReflection={msg.role === 'assistant' && !msg.streaming && !msg.error
                  ? handleSaveReflection : undefined}
              />
            ))}

            {error && (
              <div className="card border-red-500/30 bg-red-900/10 p-4 text-red-300 text-sm flex items-start gap-2">
                <span>⚠</span>
                <span>{error}</span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
          )}

          {/* Input — only shown in chat view */}
          {view === 'chat' && <div className="sticky bottom-0 bg-midnight border-t border-midnight-300">
            <div className="max-w-3xl mx-auto px-4 py-4">
              <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
              <p className="text-center text-[10px] text-text-muted mt-2">
                Shift+Enter for new line · guidance is spiritual, not medical advice
              </p>
            </div>
          </div>}
        </main>
      </div>
    </div>
  )
}
