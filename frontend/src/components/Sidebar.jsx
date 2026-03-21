import { X, BookOpen, Sparkles, ChevronRight } from 'lucide-react'

const SAMPLE_QUERIES = [
  "I feel lost and don't know my life's purpose",
  "How do I handle failure with grace?",
  "I'm consumed by anger and resentment",
  "What does the Gita say about fear?",
  "How can I practise detachment?",
  "I'm anxious about the future",
  "What is true happiness according to Krishna?",
  "How should I deal with difficult people?",
  "I'm grieving the loss of someone I love",
  "How do I balance duty and desire?",
]

const THEMES = [
  { key: 'duty',        label: 'Duty',        emoji: '⚖️' },
  { key: 'detachment',  label: 'Detachment',  emoji: '🌊' },
  { key: 'knowledge',   label: 'Knowledge',   emoji: '📚' },
  { key: 'devotion',    label: 'Devotion',    emoji: '❤️' },
  { key: 'action',      label: 'Action',      emoji: '⚡' },
  { key: 'soul',        label: 'Soul',        emoji: '✨' },
  { key: 'peace',       label: 'Peace',       emoji: '🕊️' },
  { key: 'meditation',  label: 'Meditation',  emoji: '🧘' },
]

export default function Sidebar({
  isOpen,
  onClose,
  onSampleQuery,
  apiStatus,
  messageCount,
}) {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}

      {/* Panel */}
      <aside
        className={`fixed left-0 top-0 h-full w-72 bg-midnight border-r border-midnight-300 z-30
                    overflow-y-auto transition-transform duration-300 ease-out
                    ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="p-5 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <img
                src="/images/app-icon.png"
                alt="Gita Wisdom"
                className="w-7 h-7 object-contain flex-shrink-0"
              />
              <span className="font-bold text-gold">Sacred Guide</span>
            </div>
            <button
              onClick={onClose}
              aria-label="Close sidebar"
              className="p-1.5 rounded-lg hover:bg-midnight-100 text-text-muted hover:text-cream transition-colors"
            >
              <X size={17} />
            </button>
          </div>

          {/* Status card */}
          {apiStatus && (
            <div className="card p-4 space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-xs font-semibold text-green-400">System Active</span>
              </div>
              <div className="text-xs text-text-muted space-y-1">
                <div>📖 {apiStatus.document_count.toLocaleString()} verses indexed</div>
                <div>🤖 {apiStatus.embedding_model || 'AI'} model ready</div>
                {messageCount > 0 && (
                  <div>💬 {messageCount} message{messageCount !== 1 ? 's' : ''} this session</div>
                )}
              </div>
            </div>
          )}

          {/* Explore themes */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={14} className="text-saffron" />
              <h3 className="text-xs font-semibold text-gold uppercase tracking-widest">
                Explore Themes
              </h3>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {THEMES.map((t) => (
                <button
                  key={t.key}
                  onClick={() => {
                    onSampleQuery(`Tell me about ${t.label} as taught in the Bhagavad Gita`)
                    onClose()
                  }}
                  className="p-3 card hover:border-saffron/40 hover:bg-midnight-200 transition-all
                             text-center group"
                >
                  <div className="text-xl mb-1">{t.emoji}</div>
                  <div className="text-[11px] text-text-muted group-hover:text-cream transition-colors">
                    {t.label}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Sample questions */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BookOpen size={14} className="text-saffron" />
              <h3 className="text-xs font-semibold text-gold uppercase tracking-widest">
                Sample Questions
              </h3>
            </div>
            <div className="space-y-1.5">
              {SAMPLE_QUERIES.map((q, i) => (
                <button
                  key={i}
                  onClick={() => { onSampleQuery(q); onClose() }}
                  className="w-full text-left flex items-start gap-2 p-3 rounded-xl text-xs
                             card hover:border-saffron/30 hover:bg-midnight-200 transition-all
                             text-text-muted hover:text-cream group"
                >
                  <ChevronRight
                    size={12}
                    className="text-saffron mt-0.5 flex-shrink-0 group-hover:text-gold transition-colors"
                  />
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="card p-3 border-amber-500/20 bg-amber-900/10 text-[11px] text-amber-300/80 leading-relaxed">
            ⚠️ Spiritual guidance only. For serious mental health concerns, please consult a qualified professional.
          </div>

          {/* Footer */}
          <p className="text-center text-[11px] text-text-muted pb-2">
            Made with ❤️ by <span className="text-cream-dark">Subrata Bhuin</span>
          </p>
        </div>
      </aside>
    </>
  )
}
