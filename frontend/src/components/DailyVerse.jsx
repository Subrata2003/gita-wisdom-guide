import { useState, useEffect } from 'react'
import { ChevronDown, ChevronUp, Sparkles, Share2 } from 'lucide-react'
import { getDailyVerse } from '../services/api.js'
import { shareVerseCard } from '../utils/shareCard.js'
import ReflectionInput from './ReflectionInput.jsx'

const REFLECTION_PROMPTS = {
  duty:        'How is this teaching calling you to act with integrity today?',
  detachment:  'What are you holding onto that this verse invites you to release?',
  knowledge:   'What truth within yourself does this teaching illuminate?',
  devotion:    'How might surrender and trust transform your current challenge?',
  action:      'What one action, however small, aligns with this teaching today?',
  soul:        'If you remembered your eternal nature right now — what would change?',
  peace:       'What would it mean to carry this stillness into your day?',
  meditation:  'Can you sit with this teaching for just three breaths today?',
  general:     'How does this teaching speak to where you are right now?',
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
}

export default function DailyVerse({ onQuery, onSaveReflection }) {
  const [verse, setVerse]           = useState(null)
  const [loading, setLoading]       = useState(true)
  const [showTranslit, setShowTranslit] = useState(false)
  const [collapsed, setCollapsed]   = useState(false)
  const [sharing, setSharing]       = useState(false)

  async function handleShare() {
    if (!verse) return
    setSharing(true)
    try { await shareVerseCard(verse) } catch { /* ignore */ }
    setSharing(false)
  }

  useEffect(() => {
    getDailyVerse()
      .then(setVerse)
      .catch(() => setVerse(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="max-w-2xl w-full mx-auto mb-8">
        <div className="rounded-2xl p-6 animate-pulse"
          style={{ background: 'rgba(255,215,0,0.04)', border: '1px solid rgba(255,215,0,0.15)' }}>
          <div className="h-3 w-32 rounded bg-midnight-300 mb-4" />
          <div className="h-5 w-full rounded bg-midnight-300 mb-2" />
          <div className="h-5 w-3/4 rounded bg-midnight-300" />
        </div>
      </div>
    )
  }

  if (!verse) return null

  const reflection = REFLECTION_PROMPTS[verse.theme] || REFLECTION_PROMPTS.general

  return (
    <div className="max-w-2xl w-full mx-auto mb-8 msg-enter">
      {/* Header row */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <Sparkles size={13} className="text-gold" />
          <span className="text-[11px] font-semibold uppercase tracking-widest text-gold">
            Today's Sacred Verse
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-text-muted">{formatDate(verse.date)}</span>
          {/* Share daily verse */}
          <button
            onClick={handleShare}
            disabled={sharing}
            title="Share today's verse"
            className="transition-colors disabled:opacity-40"
            style={{ color: sharing ? '#FFD700' : '#7B6FA0' }}
            onMouseEnter={e => e.currentTarget.style.color = '#FFD700'}
            onMouseLeave={e => { if (!sharing) e.currentTarget.style.color = '#7B6FA0' }}
          >
            <Share2 size={14} />
          </button>
          <button
            onClick={() => setCollapsed(v => !v)}
            className="text-text-muted hover:text-cream transition-colors"
            aria-label={collapsed ? 'Expand' : 'Collapse'}
          >
            {collapsed ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
          </button>
        </div>
      </div>

      {/* Card */}
      <div
        className="relative rounded-2xl overflow-hidden"
        style={{
          backgroundImage: 'url(/images/verse-scroll.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          border: '1px solid rgba(255,215,0,0.35)',
          boxShadow: '0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,215,0,0.08)',
        }}
      >
        {/* Darker overlay for daily card */}
        <div className="absolute inset-0 rounded-2xl"
          style={{ background: 'rgba(5,3,20,0.72)' }} />

        {/* Gold top accent — thicker for daily verse */}
        <div className="absolute top-0 left-0 right-0 h-[3px] rounded-t-2xl"
          style={{ background: 'linear-gradient(90deg, #FF8C00, #FFD700, #FF8C00)' }} />

        {/* Left accent */}
        <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-2xl"
          style={{ background: 'linear-gradient(to bottom, #FFD700, #FF8C00)' }} />

        <div className="relative z-10 px-6 pt-5 pb-5 space-y-4">
          {/* Chapter badge + theme */}
          <div className="flex items-center gap-2">
            <span
              className="text-[11px] font-bold uppercase tracking-widest px-3 py-1 rounded-full"
              style={{ background: 'rgba(255,215,0,0.12)', color: '#FFD700', border: '1px solid rgba(255,215,0,0.3)' }}
            >
              Chapter {verse.chapter} · Verse {verse.verse}
            </span>
            {verse.theme && (
              <span className="text-[11px] capitalize font-medium" style={{ color: '#E8C97A' }}>
                {verse.theme}
              </span>
            )}
          </div>

          {!collapsed && (
            <>
              {/* Sanskrit Devanagari */}
              {verse.sanskrit && (
                <div className="rounded-xl px-4 py-3 text-center"
                  style={{ background: 'rgba(255,215,0,0.07)', border: '1px solid rgba(255,215,0,0.18)' }}>
                  <p
                    className="text-[17px] leading-loose tracking-wide"
                    style={{
                      fontFamily: '"Noto Serif Devanagari", serif',
                      color: '#FFD700',
                      textShadow: '0 0 20px rgba(255,215,0,0.4)',
                    }}
                  >
                    {verse.sanskrit}
                  </p>
                </div>
              )}

              {/* Transliteration toggle */}
              {verse.sanskrit && verse.transliteration && (
                <div>
                  <button
                    onClick={() => setShowTranslit(v => !v)}
                    className="flex items-center gap-1 text-[11px] transition-colors"
                    style={{ color: '#C8A84B' }}
                    onMouseEnter={e => e.currentTarget.style.color = '#FFD700'}
                    onMouseLeave={e => e.currentTarget.style.color = '#C8A84B'}
                  >
                    {showTranslit ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                    {showTranslit ? 'Hide' : 'Show'} transliteration
                  </button>
                  {showTranslit && (
                    <p className="mt-1.5 text-[12px] leading-relaxed italic text-text-muted">
                      {verse.transliteration}
                    </p>
                  )}
                </div>
              )}

              {/* Divider */}
              {verse.sanskrit && (
                <div className="border-t border-gold/10" />
              )}

              {/* English translation */}
              <p className="text-[14px] leading-relaxed italic"
                style={{ color: '#F5E6C8', textShadow: '0 1px 4px rgba(0,0,0,0.8)' }}>
                {verse.text}
              </p>

              {/* Reflection prompt */}
              <div className="rounded-xl px-4 py-3"
                style={{ background: 'rgba(255,140,0,0.06)', border: '1px solid rgba(255,140,0,0.15)' }}>
                <p className="text-[11px] uppercase tracking-widest font-semibold mb-1"
                  style={{ color: '#FF8C00' }}>
                  Reflect
                </p>
                <p className="text-[12px] leading-relaxed" style={{ color: '#C8A84B' }}>
                  {reflection}
                </p>
              </div>

              {/* Reflection input */}
              {onSaveReflection && (
                <ReflectionInput
                  source={{
                    type:      'daily_verse',
                    chapter:   verse.chapter,
                    verse:     verse.verse,
                    verseText: verse.text,
                    sanskrit:  verse.sanskrit,
                    theme:     verse.theme,
                  }}
                  prompt={reflection}
                  onSave={onSaveReflection}
                />
              )}

              {/* CTA */}
              <button
                onClick={() => onQuery(`Explain the meaning of Chapter ${verse.chapter}, Verse ${verse.verse} and how I can apply it in my daily life`)}
                className="w-full py-2.5 rounded-xl text-[12px] font-semibold tracking-wide
                           transition-all duration-200 hover:scale-[1.02] active:scale-95"
                style={{
                  background: 'linear-gradient(135deg, rgba(255,140,0,0.15), rgba(255,215,0,0.1))',
                  border: '1px solid rgba(255,140,0,0.35)',
                  color: '#FFA533',
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(255,215,0,0.6)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,140,0,0.35)'}
              >
                Seek deeper guidance on this verse →
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
