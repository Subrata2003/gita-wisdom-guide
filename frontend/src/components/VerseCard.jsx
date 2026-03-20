export default function VerseCard({ verse }) {
  const pct = Math.min(100, Math.round((verse.relevance_score || 0) * 100))

  return (
    <div className="verse-card card p-4 hover:border-saffron/30">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          <span className="text-xs font-semibold text-saffron uppercase tracking-widest">
            Ch {verse.chapter} · V {verse.verse}
          </span>
          {verse.theme && (
            <span className="ml-2 text-xs text-text-muted capitalize">
              · {verse.theme}
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

      <p className="text-cream text-sm leading-relaxed">{verse.text}</p>
    </div>
  )
}
