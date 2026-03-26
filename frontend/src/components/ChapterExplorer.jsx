/**
 * ChapterExplorer — grid view of all 18 Bhagavad Gita chapters
 */

import { useState } from 'react'
import { CHAPTERS, THEME_COLORS } from '../data/chapters.js'
import { BookOpen } from 'lucide-react'

const THEME_FILTERS = [
  { key: null,        label: 'All' },
  { key: 'knowledge', label: '📚 Knowledge' },
  { key: 'devotion',  label: '❤️ Devotion' },
  { key: 'action',    label: '⚡ Action' },
  { key: 'detachment',label: '🌊 Detachment' },
  { key: 'meditation',label: '🧘 Meditation' },
  { key: 'soul',      label: '✨ Soul' },
  { key: 'duty',      label: '⚖️ Duty' },
]

function ChapterCard({ chapter, onClick }) {
  const [hovered, setHovered] = useState(false)
  const tc = THEME_COLORS[chapter.theme] || THEME_COLORS.general

  return (
    <button
      onClick={() => onClick(chapter)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="text-left w-full transition-all duration-200"
      style={{
        background:    hovered ? 'linear-gradient(135deg, #1e1a4a 0%, #231f56 100%)' : 'linear-gradient(135deg, #1A1640 0%, #1e1a4a 100%)',
        border:        hovered ? '1px solid rgba(255,215,0,0.4)' : '1px solid rgba(45,40,104,0.8)',
        borderRadius:  '16px',
        boxShadow:     hovered ? '0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,215,0,0.1)' : '0 4px 16px rgba(0,0,0,0.3)',
        transform:     hovered ? 'translateY(-3px)' : 'none',
        padding:       '20px',
        position:      'relative',
        overflow:      'hidden',
      }}
    >
      {/* Top accent line */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
        background: hovered
          ? 'linear-gradient(90deg, #FF8C00, #FFD700, transparent)'
          : 'linear-gradient(90deg, rgba(255,140,0,0.3), transparent)',
        borderRadius: '16px 16px 0 0',
      }} />

      {/* Chapter number */}
      <div style={{
        fontSize: '11px', fontWeight: 700, letterSpacing: '3px',
        color: 'rgba(255,215,0,0.5)', textTransform: 'uppercase', marginBottom: '10px',
      }}>
        Chapter {String(chapter.n).padStart(2, '0')}
      </div>

      {/* Emoji + Name */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', marginBottom: '8px' }}>
        <span style={{ fontSize: '22px', lineHeight: 1, flexShrink: 0 }}>{chapter.emoji}</span>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: '#F5E6C8', lineHeight: 1.3 }}>
            {chapter.name}
          </div>
          <div style={{ fontSize: '11px', color: 'rgba(255,215,0,0.6)', marginTop: '3px',
            fontFamily: '"Noto Serif Devanagari", serif' }}>
            {chapter.sanskrit}
          </div>
        </div>
      </div>

      {/* Summary */}
      <p style={{
        fontSize: '11px', lineHeight: 1.6, color: '#7B6FA0',
        marginBottom: '12px', display: '-webkit-box',
        WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
      }}>
        {chapter.summary}
      </p>

      {/* Footer: theme badge + verse count */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{
          fontSize: '10px', fontWeight: 600, padding: '3px 10px',
          borderRadius: '999px', textTransform: 'capitalize',
          background: tc.bg, border: `1px solid ${tc.border}`, color: tc.text,
        }}>
          {chapter.theme}
        </span>
        <span style={{ fontSize: '11px', color: 'rgba(255,215,0,0.45)' }}>
          {chapter.verses} verses
        </span>
      </div>
    </button>
  )
}

export default function ChapterExplorer({ onSelectChapter }) {
  const [activeTheme, setActiveTheme] = useState(null)

  const filtered = activeTheme
    ? CHAPTERS.filter(c => c.theme === activeTheme)
    : CHAPTERS

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">

      {/* Page header */}
      <div className="flex items-center gap-3 mb-6">
        <div style={{
          width: 44, height: 44, borderRadius: 12, flexShrink: 0,
          background: 'rgba(255,215,0,0.1)', border: '1px solid rgba(255,215,0,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <BookOpen size={20} style={{ color: '#FFD700' }} />
        </div>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#FFD700' }}>Chapter Explorer</h1>
          <p style={{ fontSize: '12px', color: '#7B6FA0' }}>
            18 chapters · 640 verses · The complete Bhagavad Gita
          </p>
        </div>
      </div>

      {/* Theme filter pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '28px' }}>
        {THEME_FILTERS.map(f => {
          const active = activeTheme === f.key
          return (
            <button
              key={String(f.key)}
              onClick={() => setActiveTheme(f.key)}
              style={{
                fontSize: '11px', fontWeight: 600, padding: '6px 14px',
                borderRadius: '999px', cursor: 'pointer', transition: 'all 0.15s',
                background: active ? 'rgba(255,215,0,0.15)' : 'rgba(255,255,255,0.04)',
                border:     active ? '1px solid rgba(255,215,0,0.5)' : '1px solid rgba(255,255,255,0.1)',
                color:      active ? '#FFD700' : '#7B6FA0',
              }}
            >
              {f.label}
            </button>
          )
        })}
      </div>

      {/* Chapter grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
        gap: '16px',
      }}>
        {filtered.map(ch => (
          <ChapterCard key={ch.n} chapter={ch} onClick={onSelectChapter} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', color: '#7B6FA0' }}>
          No chapters match this filter.
        </div>
      )}
    </div>
  )
}
