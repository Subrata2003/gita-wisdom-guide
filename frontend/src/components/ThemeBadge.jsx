const THEME_CONFIG = {
  duty:       { emoji: '⚖️', cls: 'text-blue-300   bg-blue-900/25   border-blue-500/30'   },
  detachment: { emoji: '🌊', cls: 'text-cyan-300    bg-cyan-900/25   border-cyan-500/30'   },
  knowledge:  { emoji: '📚', cls: 'text-yellow-300  bg-yellow-900/25 border-yellow-500/30' },
  devotion:   { emoji: '❤️', cls: 'text-rose-300    bg-rose-900/25   border-rose-500/30'   },
  action:     { emoji: '⚡', cls: 'text-orange-300  bg-orange-900/25 border-orange-500/30' },
  soul:       { emoji: '✨', cls: 'text-purple-300  bg-purple-900/25 border-purple-500/30' },
  peace:      { emoji: '🕊️', cls: 'text-green-300   bg-green-900/25  border-green-500/30'  },
  meditation: { emoji: '🧘', cls: 'text-indigo-300  bg-indigo-900/25 border-indigo-500/30' },
  general:    { emoji: '🕉️', cls: 'text-amber-300   bg-amber-900/25  border-amber-500/30'  },
}

export default function ThemeBadge({ theme }) {
  const cfg = THEME_CONFIG[theme] || THEME_CONFIG.general
  return (
    <span className={`theme-badge ${cfg.cls}`}>
      <span>{cfg.emoji}</span>
      {theme.charAt(0).toUpperCase() + theme.slice(1)}
    </span>
  )
}
