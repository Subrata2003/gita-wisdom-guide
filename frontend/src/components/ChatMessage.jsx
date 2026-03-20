import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import VerseCard from './VerseCard.jsx'
import ThemeBadge from './ThemeBadge.jsx'
import { ChevronDown, ChevronUp } from 'lucide-react'

function formatTime(date) {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function ChatMessage({ message }) {
  const [versesOpen, setVersesOpen] = useState(false)
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end msg-enter">
        <div
          className="max-w-[82%] bg-gradient-to-br from-saffron/15 to-gold/10
                     border border-saffron/25 rounded-2xl rounded-tr-none px-5 py-4"
        >
          <p className="text-cream leading-relaxed text-sm whitespace-pre-wrap">
            {message.content}
          </p>
          <p className="text-[10px] text-text-muted mt-2 text-right">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    )
  }

  // Assistant message
  return (
    <div className="flex items-start gap-3 msg-enter">
      {/* Avatar */}
      <div
        className="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center text-base
                   bg-gradient-to-br from-saffron to-gold shadow-saffron"
      >
        🕉️
      </div>

      <div className="flex-1 min-w-0 space-y-3">
        {/* Response bubble */}
        <div
          className={`card px-5 py-5 rounded-2xl rounded-tl-none ${
            message.error ? 'border-red-500/30 bg-red-900/10' : ''
          }`}
        >
          {message.error && (
            <p className="text-red-400 text-xs font-medium mb-2">
              ⚠ Partial response — LLM encountered an issue
            </p>
          )}
          <div className="wisdom-prose">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          <p className="text-[10px] text-text-muted mt-3">
            {formatTime(message.timestamp)}
          </p>
        </div>

        {/* Theme badges */}
        {message.themes?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.themes.map((t) => (
              <ThemeBadge key={t} theme={t} />
            ))}
          </div>
        )}

        {/* Verse accordion */}
        {message.verses?.length > 0 && (
          <div>
            <button
              onClick={() => setVersesOpen((v) => !v)}
              className="flex items-center gap-1.5 text-xs text-saffron hover:text-gold
                         transition-colors font-medium"
            >
              {versesOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              {versesOpen ? 'Hide' : 'View'} {message.verses.length} referenced{' '}
              {message.verses.length === 1 ? 'verse' : 'verses'}
            </button>

            {versesOpen && (
              <div className="mt-3 space-y-2">
                {message.verses.map((v, i) => (
                  <VerseCard key={i} verse={v} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
