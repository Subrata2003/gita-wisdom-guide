import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import VerseCard from './VerseCard.jsx'
import ThemeBadge from './ThemeBadge.jsx'
import ReflectionInput from './ReflectionInput.jsx'
import { ChevronDown, ChevronUp } from 'lucide-react'

const MOOD_CONFIG = {
  grief:     { emoji: '💙', label: 'Grief',     color: 'rgba(147,197,253,0.7)' },
  anger:     { emoji: '🔥', label: 'Anger',     color: 'rgba(252,165,165,0.7)' },
  anxiety:   { emoji: '🌀', label: 'Anxiety',   color: 'rgba(196,181,253,0.7)' },
  confusion: { emoji: '🔍', label: 'Seeking',   color: 'rgba(253,211,77,0.7)'  },
  despair:   { emoji: '🌑', label: 'Despair',   color: 'rgba(148,163,184,0.7)' },
  longing:   { emoji: '🌙', label: 'Longing',   color: 'rgba(221,214,254,0.7)' },
  curiosity: { emoji: '✨', label: 'Curiosity', color: 'rgba(255,215,0,0.7)'   },
}

function formatTime(date) {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function ChatMessage({ message, onSaveReflection }) {
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
      {/* Avatar — transparent PNG, no background needed */}
      <div className="w-9 h-9 flex-shrink-0 flex items-center justify-center">
        <img
          src="/images/chat_app_logo.png"
          alt="Krishna"
          className="w-full h-full object-contain"
        />
      </div>

      <div className="flex-1 min-w-0 space-y-3">
        {/* Response bubble */}
        <div
          className={`relative rounded-2xl rounded-tl-none overflow-hidden ${
            message.error ? 'border border-red-500/30 bg-red-900/10' : ''
          }`}
          style={message.error ? {} : {
            background: 'linear-gradient(135deg, #1A1640 0%, #1e1a4a 100%)',
            boxShadow: '0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,140,0,0.08)',
            border: '1px solid rgba(45,40,104,0.8)',
          }}
        >
          {/* Saffron accent line at top */}
          {!message.error && (
            <div
              className="absolute top-0 left-0 right-0 h-[2px] rounded-t-2xl"
              style={{ background: 'linear-gradient(90deg, #FF8C00, #FFD700, transparent)' }}
            />
          )}

          <div className="px-5 py-5">
            {message.error && (
              <p className="text-red-400 text-xs font-medium mb-2">
                ⚠ Partial response — LLM encountered an issue
              </p>
            )}

            {/* Waiting for first token: show typing dots */}
            {message.streaming && message.content === '' ? (
              <div className="flex items-center gap-2 py-1">
                <span className="text-xs text-text-muted">Reflecting on wisdom</span>
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-saffron dot-1" />
                  <div className="w-2 h-2 rounded-full bg-saffron dot-2" />
                  <div className="w-2 h-2 rounded-full bg-saffron dot-3" />
                </div>
              </div>
            ) : message.streaming ? (
              /* Streaming: plain text + blinking cursor */
              <div className="wisdom-prose">
                <span className="whitespace-pre-wrap text-sm leading-relaxed text-cream">
                  {message.content}
                </span>
                <span
                  className="inline-block w-[2px] h-[1.1em] bg-gold ml-[2px] align-middle"
                  style={{ animation: 'pulse 1s ease-in-out infinite' }}
                />
              </div>
            ) : (
              /* Done: full markdown rendering */
              <div className="wisdom-prose">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}

            {!message.streaming && (
              <div className="flex items-center justify-between mt-3 gap-3">
                <p className="text-[10px] text-text-muted">{formatTime(message.timestamp)}</p>
                {onSaveReflection && (
                  <ReflectionInput
                    source={{
                      type:      'chat',
                      query:     message.query,
                      chapter:   message.verses?.[0]?.chapter,
                      verse:     message.verses?.[0]?.verse,
                      verseText: message.verses?.[0]?.text,
                      sanskrit:  message.verses?.[0]?.sanskrit,
                      theme:     message.verses?.[0]?.theme,
                    }}
                    prompt="What does this teaching stir in you?"
                    onSave={onSaveReflection}
                  />
                )}
              </div>
            )}
          </div>
        </div>

        {/* Mood badge — shown only when a non-neutral mood was detected */}
        {!message.streaming && message.mood && MOOD_CONFIG[message.mood] && (
          <div className="flex items-center gap-1.5">
            <span style={{
              fontSize: '10px', padding: '2px 9px', borderRadius: '999px',
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
              color: MOOD_CONFIG[message.mood].color,
              display: 'inline-flex', alignItems: 'center', gap: '4px',
            }}>
              {MOOD_CONFIG[message.mood].emoji} {MOOD_CONFIG[message.mood].label}
            </span>
            <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.2)' }}>·</span>
            <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)' }}>tone adapted</span>
          </div>
        )}

        {/* Theme badges and verse accordion appear only after streaming is done */}
        {message.themes?.length > 0 && !message.streaming && (
          <div className="flex flex-wrap gap-1.5">
            {message.themes.map((t) => (
              <ThemeBadge key={t} theme={t} />
            ))}
          </div>
        )}

        {/* Verse accordion */}
        {message.verses?.length > 0 && !message.streaming && (
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
