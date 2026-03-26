/**
 * ChapterDetail — all verses for one Bhagavad Gita chapter
 */

import { useState, useEffect } from 'react'
import { ChevronDown, ChevronUp, ArrowLeft, Share2 } from 'lucide-react'
import { THEME_COLORS } from '../data/chapters.js'
import { shareVerseCard } from '../utils/shareCard.js'
import ReflectionInput from './ReflectionInput.jsx'

const BASE = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''

function VerseRow({ verse, onAskKrishna, onSaveReflection }) {
  const [open, setOpen]             = useState(false)
  const [showTranslit, setShowTranslit] = useState(false)
  const [sharing, setSharing]       = useState(false)
  const tc = THEME_COLORS[verse.theme] || THEME_COLORS.general

  async function handleShare() {
    setSharing(true)
    try { await shareVerseCard(verse) } catch { /* ignore */ }
    setSharing(false)
  }

  return (
    <div
      style={{
        background: open ? 'linear-gradient(135deg, #1e1a4a 0%, #231f56 100%)' : 'linear-gradient(135deg, #1A1640 0%, #1e1a4a 100%)',
        border: open ? '1px solid rgba(255,215,0,0.3)' : '1px solid rgba(45,40,104,0.8)',
        borderRadius: '14px',
        overflow: 'hidden',
        transition: 'all 0.2s',
      }}
    >
      {/* Collapsed row — click to expand */}
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full text-left"
        style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '12px' }}
      >
        {/* Verse number badge */}
        <span style={{
          fontSize: '11px', fontWeight: 700, padding: '3px 10px', borderRadius: '999px',
          flexShrink: 0, letterSpacing: '1px',
          background: 'rgba(255,140,0,0.12)', border: '1px solid rgba(255,140,0,0.3)', color: '#FF8C00',
        }}>
          {verse.chapter}.{verse.verse}
        </span>

        {/* Preview text */}
        <p style={{
          flex: 1, fontSize: '13px', color: open ? '#F5E6C8' : '#B8A48C',
          lineHeight: 1.4, textAlign: 'left',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {verse.text}
        </p>

        {/* Theme + chevron */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          <span style={{
            fontSize: '10px', padding: '2px 8px', borderRadius: '999px', textTransform: 'capitalize',
            background: tc.bg, border: `1px solid ${tc.border}`, color: tc.text,
          }}>{verse.theme}</span>
          {open ? <ChevronUp size={14} style={{ color: '#7B6FA0' }} /> : <ChevronDown size={14} style={{ color: '#7B6FA0' }} />}
        </div>
      </button>

      {/* Expanded content */}
      {open && (
        <div style={{ padding: '0 18px 18px', borderTop: '1px solid rgba(255,215,0,0.08)' }}>

          {/* Sanskrit */}
          {verse.sanskrit && (
            <div style={{
              margin: '14px 0 10px',
              background: 'rgba(255,215,0,0.06)', border: '1px solid rgba(255,215,0,0.15)',
              borderRadius: '10px', padding: '12px 16px', textAlign: 'center',
            }}>
              <p style={{
                fontFamily: '"Noto Serif Devanagari", serif',
                fontSize: '16px', lineHeight: 1.9, letterSpacing: '0.5px',
                color: '#FFD700', textShadow: '0 0 20px rgba(255,215,0,0.3)',
              }}>
                {verse.sanskrit}
              </p>
            </div>
          )}

          {/* Transliteration toggle */}
          {verse.transliteration && (
            <div style={{ marginBottom: '10px' }}>
              <button
                onClick={() => setShowTranslit(v => !v)}
                style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#C8A84B', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                {showTranslit ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
                {showTranslit ? 'Hide' : 'Show'} transliteration
              </button>
              {showTranslit && (
                <p style={{ fontSize: '12px', fontStyle: 'italic', color: '#7B6FA0', marginTop: '6px', lineHeight: 1.6 }}>
                  {verse.transliteration}
                </p>
              )}
            </div>
          )}

          {/* Divider */}
          {verse.sanskrit && <div style={{ height: '1px', background: 'rgba(255,215,0,0.08)', margin: '10px 0' }} />}

          {/* English */}
          <p style={{ fontSize: '13px', lineHeight: 1.7, fontStyle: 'italic', color: '#F5E6C8', marginBottom: '14px' }}>
            {verse.text}
          </p>

          {/* Actions */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
            <button
              onClick={() => onAskKrishna(verse)}
              style={{
                fontSize: '12px', fontWeight: 600, padding: '7px 16px', borderRadius: '10px',
                background: 'linear-gradient(135deg, rgba(255,140,0,0.15), rgba(255,215,0,0.1))',
                border: '1px solid rgba(255,140,0,0.35)', color: '#FFA533', cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              Ask Krishna about this verse →
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {onSaveReflection && (
                <ReflectionInput
                  source={{
                    type: 'daily_verse',
                    chapter: verse.chapter,
                    verse: verse.verse,
                    verseText: verse.text,
                    sanskrit: verse.sanskrit,
                    theme: verse.theme,
                  }}
                  prompt="What does this teaching stir in you?"
                  onSave={onSaveReflection}
                />
              )}
              <button
                onClick={handleShare}
                disabled={sharing}
                title="Share this verse"
                style={{ color: sharing ? '#FFD700' : '#7B6FA0', background: 'none', border: 'none', cursor: 'pointer', transition: 'color 0.15s' }}
              >
                <Share2 size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ChapterDetail({ chapter, onBack, onAskKrishna, onSaveReflection }) {
  const [verses, setVerses]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const tc = THEME_COLORS[chapter.theme] || THEME_COLORS.general

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetch(`${BASE}/api/chapter/${chapter.n}/verses`)
      .then(r => { if (!r.ok) throw new Error('Failed to load'); return r.json() })
      .then(data => setVerses(data.verses || []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [chapter.n])

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">

      {/* Back button */}
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#7B6FA0', background: 'none', border: 'none', cursor: 'pointer', marginBottom: '20px', padding: 0 }}
        onMouseEnter={e => e.currentTarget.style.color = '#F5E6C8'}
        onMouseLeave={e => e.currentTarget.style.color = '#7B6FA0'}
      >
        <ArrowLeft size={13} /> Back to Chapters
      </button>

      {/* Chapter header */}
      <div style={{
        background: 'linear-gradient(135deg, #1A1640 0%, #231f56 100%)',
        border: '1px solid rgba(255,215,0,0.2)',
        borderRadius: '18px', padding: '24px', marginBottom: '24px', position: 'relative', overflow: 'hidden',
      }}>
        {/* Gold top accent */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px',
          background: 'linear-gradient(90deg, #FF8C00, #FFD700, #FF8C00)', borderRadius: '18px 18px 0 0' }} />

        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
          <span style={{ fontSize: '36px', lineHeight: 1, flexShrink: 0 }}>{chapter.emoji}</span>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '6px' }}>
              <span style={{
                fontSize: '11px', fontWeight: 700, letterSpacing: '2px',
                padding: '3px 12px', borderRadius: '999px',
                background: 'rgba(255,140,0,0.12)', border: '1px solid rgba(255,140,0,0.3)', color: '#FF8C00',
              }}>
                CHAPTER {chapter.n}
              </span>
              <span style={{
                fontSize: '10px', padding: '3px 10px', borderRadius: '999px', textTransform: 'capitalize',
                background: tc.bg, border: `1px solid ${tc.border}`, color: tc.text,
              }}>
                {chapter.theme}
              </span>
            </div>

            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#FFD700', marginBottom: '4px' }}>
              {chapter.name}
            </h2>
            <p style={{ fontSize: '13px', color: 'rgba(255,215,0,0.55)',
              fontFamily: '"Noto Serif Devanagari", serif', marginBottom: '10px' }}>
              {chapter.sanskrit}
            </p>
            <p style={{ fontSize: '13px', lineHeight: 1.7, color: '#B8A48C' }}>
              {chapter.summary}
            </p>
            <p style={{ fontSize: '11px', color: '#7B6FA0', marginTop: '10px' }}>
              {chapter.verses} verses
            </p>
          </div>
        </div>
      </div>

      {/* Verses list */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[...Array(6)].map((_, i) => (
            <div key={i} style={{ height: '52px', borderRadius: '14px',
              background: 'rgba(255,215,0,0.04)', border: '1px solid rgba(255,215,0,0.08)',
              animation: 'pulse 2s infinite' }} />
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '20px', textAlign: 'center', color: '#FC8181', fontSize: '13px' }}>
          ⚠ {error}
        </div>
      )}

      {!loading && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {verses.map(v => (
            <VerseRow
              key={`${v.chapter}-${v.verse}`}
              verse={v}
              onAskKrishna={onAskKrishna}
              onSaveReflection={onSaveReflection}
            />
          ))}
        </div>
      )}
    </div>
  )
}
