import { useState, useRef, useEffect } from 'react'
import { Menu, PlusCircle, History, X } from 'lucide-react'

export default function Header({ onMenuClick, apiStatus, messages = [], onNewChat }) {
  const [historyOpen, setHistoryOpen] = useState(false)
  const panelRef = useRef(null)

  const userMessages = messages.filter((m) => m.role === 'user')

  // Close panel on outside click
  useEffect(() => {
    if (!historyOpen) return
    function handleClick(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setHistoryOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [historyOpen])

  return (
    <header className="relative z-10 border-b border-midnight-300 bg-midnight/80 backdrop-blur-xl flex-shrink-0">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">

        {/* Left: hamburger + logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            aria-label="Open menu"
            className="p-2 rounded-lg hover:bg-midnight-100 transition-colors text-text-muted hover:text-cream"
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-2.5">
            <img
              src="/images/app-icon.png"
              alt="Gita Wisdom Guide"
              className="w-9 h-9 object-contain flex-shrink-0"
            />
            <div>
              <h1 className="text-base font-bold leading-tight bg-gradient-to-r from-saffron to-gold bg-clip-text text-transparent">
                Gita Wisdom Guide
              </h1>
              <p className="text-[11px] text-text-muted leading-none mt-0.5">
                Ancient wisdom · Modern life
              </p>
            </div>
          </div>
        </div>

        {/* Right: actions + status */}
        <div className="flex items-center gap-2">

          {/* History button — only when there are messages */}
          {userMessages.length > 0 && (
            <div className="relative" ref={panelRef}>
              <button
                onClick={() => setHistoryOpen((o) => !o)}
                aria-label="Session history"
                title="This session's history"
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium
                            transition-colors border
                            ${historyOpen
                              ? 'bg-midnight-200 border-saffron/30 text-saffron'
                              : 'border-midnight-300 text-text-muted hover:text-cream hover:bg-midnight-100'}`}
              >
                <History size={14} />
                <span className="hidden sm:inline">History</span>
                <span className="text-[10px] bg-saffron/20 text-saffron px-1.5 py-0.5 rounded-full">
                  {userMessages.length}
                </span>
              </button>

              {/* History dropdown panel */}
              {historyOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-midnight border border-midnight-300
                                rounded-xl shadow-2xl z-50 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-midnight-300">
                    <span className="text-xs font-semibold text-gold uppercase tracking-widest">
                      This Session
                    </span>
                    <button
                      onClick={() => setHistoryOpen(false)}
                      className="text-text-muted hover:text-cream transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </div>

                  <div className="max-h-72 overflow-y-auto divide-y divide-midnight-300">
                    {userMessages.map((msg, i) => (
                      <div key={i} className="px-4 py-3 hover:bg-midnight-100 transition-colors">
                        <p className="text-xs text-cream-dark line-clamp-2 leading-relaxed">
                          {msg.content}
                        </p>
                        <p className="text-[10px] text-text-muted mt-1">
                          {msg.timestamp
                            ? new Date(msg.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : ''}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="px-4 py-3 border-t border-midnight-300 bg-midnight-100">
                    <p className="text-[10px] text-text-muted text-center">
                      Full history available after login feature is added
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* New Chat button — only when there are messages */}
          {messages.length > 0 && (
            <button
              onClick={() => { onNewChat(); setHistoryOpen(false) }}
              aria-label="Start new chat"
              title="Start a new conversation"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                         border border-saffron/30 bg-saffron/10 text-saffron
                         hover:bg-saffron/20 transition-colors"
            >
              <PlusCircle size={14} />
              <span className="hidden sm:inline">New Chat</span>
            </button>
          )}

          {/* Status pill */}
          {apiStatus ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-900/20 border border-green-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-[11px] text-green-400 font-medium hidden sm:inline">
                {apiStatus.document_count.toLocaleString()} verses
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-900/20 border border-red-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
              <span className="text-[11px] text-red-400 font-medium hidden sm:inline">
                Backend offline
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
