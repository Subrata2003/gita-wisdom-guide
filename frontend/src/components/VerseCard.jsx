import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

export default function VerseCard({ verse }) {
  const [showTranslit, setShowTranslit] = useState(false)
  const pct = Math.min(100, Math.round((verse.relevance_score || 0) * 100))
  const hasSanskrit = !!verse.sanskrit

  return (
    <div
      className="verse-card relative rounded-2xl overflow-hidden"
      style={{
        backgroundImage: 'url(/images/verse-scroll.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        border: '1px solid rgba(255,140,0,0.3)',
        boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
      }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 rounded-2xl" style={{ background: 'rgba(0,0,0,0.58)' }} />
      {/* Saffron left accent */}
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-2xl z-10"
        style={{ background: 'linear-gradient(to bottom, #FF8C00, #FFD700)' }}
      />

      <div className="pl-4 pr-4 pt-4 pb-3 relative z-10 space-y-3">

        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className="text-[11px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full"
              style={{ background: 'rgba(255,140,0,0.15)', color: '#FF8C00', border: '1px solid rgba(255,140,0,0.3)' }}
            >
              Ch {verse.chapter} · V {verse.verse}
            </span>
            {verse.theme && (
              <span className="text-[11px] capitalize font-medium" style={{ color: '#E8C97A' }}>{verse.theme}</span>
            )}
          </div>
          {pct > 0 && (
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <div className="w-14 h-1 bg-midnight-300 rounded-full overflow-hidden">
                <div
                  className="relevance-bar h-full bg-gradient-to-r from-saffron to-gold rounded-full"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-[10px] font-semibold" style={{ color: '#E8C97A' }}>{pct}%</span>
            </div>
          )}
        </div>

        {/* Sanskrit shloka in Devanagari */}
        {hasSanskrit && (
          <div
            className="rounded-xl px-3 py-2.5"
            style={{ background: 'rgba(255,215,0,0.06)', border: '1px solid rgba(255,215,0,0.15)' }}
          >
            <p
              className="text-[15px] leading-loose tracking-wide text-center"
              style={{
                fontFamily: '"Noto Serif Devanagari", serif',
                color: '#FFD700',
                textShadow: '0 1px 6px rgba(255,215,0,0.3)',
              }}
            >
              {verse.sanskrit}
            </p>
          </div>
        )}

        {/* IAST transliteration — collapsed by default */}
        {hasSanskrit && verse.transliteration && (
          <div>
            <button
              onClick={() => setShowTranslit((v) => !v)}
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

        {/* Divider between Sanskrit and English */}
        {hasSanskrit && (
          <div className="border-t border-saffron/10" />
        )}

        {/* English translation */}
        <p
          className="text-[13px] leading-relaxed italic"
          style={{ color: '#F5E6C8', textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}
        >
          {verse.text}
        </p>

      </div>
    </div>
  )
}
