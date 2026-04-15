/**
 * JournalPage — personal spiritual diary
 *
 * Displays all saved reflections in reverse chronological order,
 * grouped by date, with the verse reference that inspired each one.
 */

import { useState } from 'react'
import { BookOpen, Trash2, ChevronDown, ChevronUp, PenLine, Download } from 'lucide-react'
import { exportJournalToPDF } from '../utils/exportJournal.js'
import { toast } from '../utils/toast.js'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
}

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function groupByDate(entries) {
  const groups = {}
  for (const e of entries) {
    const key = new Date(e.timestamp).toDateString()
    if (!groups[key]) groups[key] = []
    groups[key].push(e)
  }
  return groups
}

function EntryCard({ entry, onDelete }) {
  const [showVerse, setShowVerse] = useState(false)
  const s = entry.source

  return (
    <div
      className="rounded-2xl overflow-hidden transition-all"
      style={{
        background: 'linear-gradient(135deg, #1A1640 0%, #1e1a4a 100%)',
        border: '1px solid rgba(45,40,104,0.8)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      }}
    >
      {/* Top accent */}
      <div className="h-[2px]" style={{ background: 'linear-gradient(90deg, #FF8C00, #FFD700, transparent)' }} />

      <div className="p-4 space-y-3">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            {/* Verse badge */}
            <span
              className="text-[10px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full"
              style={{ background: 'rgba(255,140,0,0.12)', color: '#FF8C00', border: '1px solid rgba(255,140,0,0.3)' }}
            >
              Ch {s.chapter} · V {s.verse}
            </span>
            {/* Source type */}
            <span className="text-[10px] capitalize" style={{ color: '#7B6FA0' }}>
              {s.type === 'daily_verse' ? '✦ Daily Verse' : '✦ Conversation'}
            </span>
            {s.theme && (
              <span className="text-[10px] capitalize" style={{ color: '#C8A84B' }}>{s.theme}</span>
            )}
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-[10px] text-text-muted">{formatTime(entry.timestamp)}</span>
            <button
              onClick={() => onDelete(entry.id)}
              className="p-1 rounded-lg text-text-muted hover:text-red-400 transition-colors"
              title="Delete reflection"
            >
              <Trash2 size={12} />
            </button>
          </div>
        </div>

        {/* The reflection text */}
        <p className="text-[13px] leading-relaxed" style={{ color: '#F5E6C8' }}>
          {entry.reflection}
        </p>

        {/* Collapsible verse context */}
        <button
          onClick={() => setShowVerse(v => !v)}
          className="flex items-center gap-1 text-[11px] transition-colors"
          style={{ color: '#7B6FA0' }}
          onMouseEnter={e => e.currentTarget.style.color = '#C8A84B'}
          onMouseLeave={e => e.currentTarget.style.color = '#7B6FA0'}
        >
          {showVerse ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          {showVerse ? 'Hide' : 'Show'} verse context
        </button>

        {showVerse && (
          <div
            className="rounded-xl p-3 space-y-2"
            style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,215,0,0.08)' }}
          >
            {s.query && (
              <p className="text-[11px] italic" style={{ color: '#7B6FA0' }}>
                Question: "{s.query}"
              </p>
            )}
            {s.sanskrit && (
              <p
                className="text-[13px] leading-loose text-center"
                style={{ fontFamily: '"Noto Serif Devanagari", serif', color: '#FFD700', opacity: 0.8 }}
              >
                {s.sanskrit}
              </p>
            )}
            <p className="text-[12px] leading-relaxed italic" style={{ color: '#B8A48C' }}>
              {s.verseText}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default function JournalPage({ entries, onDelete }) {
  const grouped = groupByDate(entries)
  const dates   = Object.keys(grouped)

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">

      {/* Page header */}
      <div className="flex items-center gap-3 mb-8">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: 'rgba(255,215,0,0.1)', border: '1px solid rgba(255,215,0,0.2)' }}
        >
          <BookOpen size={18} style={{ color: '#FFD700' }} />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold" style={{ color: '#FFD700' }}>Reflection Journal</h1>
          <p className="text-[12px] text-text-muted">
            {entries.length === 0
              ? 'Your personal spiritual diary'
              : `${entries.length} reflection${entries.length !== 1 ? 's' : ''} saved`}
          </p>
        </div>

        {/* Export PDF button — only shown when there are entries */}
        {entries.length > 0 && (
          <button
            onClick={() => { exportJournalToPDF(entries); toast('Journal downloaded as PDF') }}
            className="flex items-center gap-2 px-3 py-2 rounded-xl text-[12px] font-medium
                       transition-all hover:scale-105 active:scale-95"
            style={{
              background: 'rgba(255,215,0,0.08)',
              border: '1px solid rgba(255,215,0,0.25)',
              color: '#FFD700',
            }}
            title="Export journal as PDF"
          >
            <Download size={13} />
            Export PDF
          </button>
        )}
      </div>

      {/* Empty state */}
      {entries.length === 0 && (
        <div
          className="rounded-2xl p-10 text-center space-y-3"
          style={{ border: '1px dashed rgba(255,215,0,0.2)', background: 'rgba(255,215,0,0.02)' }}
        >
          <PenLine size={32} className="mx-auto" style={{ color: 'rgba(255,215,0,0.3)' }} />
          <p className="text-[14px] font-medium" style={{ color: '#C8A84B' }}>
            Your journal is empty
          </p>
          <p className="text-[12px] text-text-muted max-w-xs mx-auto leading-relaxed">
            After receiving wisdom or reading today's verse, click <strong>"Add reflection"</strong> to record what the teaching stirs in you.
          </p>
        </div>
      )}

      {/* Entries grouped by date */}
      {dates.map(date => (
        <div key={date} className="mb-8">
          {/* Date divider */}
          <div className="flex items-center gap-3 mb-4">
            <div className="h-px flex-1" style={{ background: 'rgba(255,215,0,0.1)' }} />
            <span className="text-[11px] uppercase tracking-widest font-semibold" style={{ color: '#C8A84B' }}>
              {formatDate(grouped[date][0].timestamp)}
            </span>
            <div className="h-px flex-1" style={{ background: 'rgba(255,215,0,0.1)' }} />
          </div>

          {/* Entries for this date */}
          <div className="space-y-3">
            {grouped[date].map(e => (
              <EntryCard key={e.id} entry={e} onDelete={onDelete} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
