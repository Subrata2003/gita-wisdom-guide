export default function VerseCard({ verse }) {
  const pct = Math.min(100, Math.round((verse.relevance_score || 0) * 100))

  return (
    <div
      className="verse-card relative rounded-2xl overflow-hidden p-4"
      style={{
        backgroundImage: 'url(/images/verse-scroll.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        border: '1px solid rgba(255,140,0,0.3)',
        boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
      }}
    >
      {/* Dark overlay so text stays readable over the parchment */}
      <div
        className="absolute inset-0 rounded-2xl"
        style={{ background: 'rgba(0,0,0,0.52)' }}
      />
      {/* Thin gradient left accent — sits above overlay */}
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-2xl z-10"
        style={{ background: 'linear-gradient(to bottom, #FF8C00, #FFD700)' }}
      />

      <div className="pl-2 relative z-10">
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className="text-[11px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full"
              style={{ background: 'rgba(255,140,0,0.15)', color: '#FF8C00', border: '1px solid rgba(255,140,0,0.3)' }}
            >
              Ch {verse.chapter} · V {verse.verse}
            </span>
            {verse.theme && (
              <span className="text-[11px] text-text-muted capitalize">
                {verse.theme}
              </span>
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
              <span className="text-[10px] text-text-muted">{pct}%</span>
            </div>
          )}
        </div>

        <p className="text-cream text-[13px] leading-relaxed italic" style={{ color: '#F5E6C8', textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>{verse.text}</p>
      </div>
    </div>
  )
}
