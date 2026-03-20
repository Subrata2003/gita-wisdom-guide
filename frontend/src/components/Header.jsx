import { Menu } from 'lucide-react'

export default function Header({ onMenuClick, apiStatus }) {
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
            <span className="text-2xl leading-none select-none">🕉️</span>
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

        {/* Right: status pill */}
        <div className="flex items-center gap-2">
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
