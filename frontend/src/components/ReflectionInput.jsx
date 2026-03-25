/**
 * ReflectionInput
 *
 * Embeddable reflection widget — used inside ChatMessage and DailyVerse.
 * Shows "Add reflection" link → expands textarea → saves to journal.
 *
 * Props:
 *   source      object   — journal entry source metadata
 *   prompt      string   — e.g. "What does this teaching stir in you?"
 *   onSave      fn(text, source) — called after successful save
 */

import { useState, useRef, useEffect } from 'react'
import { PenLine, Check, X } from 'lucide-react'

export default function ReflectionInput({ source, prompt, onSave }) {
  const [open, setOpen]       = useState(false)
  const [text, setText]       = useState('')
  const [saved, setSaved]     = useState(false)
  const textareaRef           = useRef(null)

  useEffect(() => {
    if (open && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [open])

  function handleSave() {
    if (!text.trim()) return
    onSave(text.trim(), source)
    setSaved(true)
    setOpen(false)
    setText('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSave()
    if (e.key === 'Escape') { setOpen(false); setText('') }
  }

  // After saving, show "Saved ✓" for 2s then reset
  useEffect(() => {
    if (!saved) return
    const t = setTimeout(() => setSaved(false), 2500)
    return () => clearTimeout(t)
  }, [saved])

  if (saved) {
    return (
      <div className="flex items-center gap-1.5 text-[11px]" style={{ color: '#4ade80' }}>
        <Check size={12} />
        <span>Reflection saved to your journal</span>
      </div>
    )
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 text-[11px] transition-colors"
        style={{ color: '#7B6FA0' }}
        onMouseEnter={e => e.currentTarget.style.color = '#C8A84B'}
        onMouseLeave={e => e.currentTarget.style.color = '#7B6FA0'}
      >
        <PenLine size={11} />
        <span>Add reflection</span>
      </button>
    )
  }

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ border: '1px solid rgba(255,140,0,0.25)', background: 'rgba(255,140,0,0.04)' }}
    >
      {/* Prompt */}
      <div className="px-3 pt-3 pb-1">
        <p className="text-[11px] italic" style={{ color: '#C8A84B' }}>{prompt}</p>
      </div>

      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Write your reflection here…"
        rows={3}
        className="w-full bg-transparent px-3 py-2 text-[13px] leading-relaxed resize-none
                   placeholder:text-text-muted outline-none"
        style={{ color: '#F5E6C8' }}
      />

      {/* Action row */}
      <div className="flex items-center justify-between px-3 pb-3">
        <span className="text-[10px] text-text-muted">Ctrl+Enter to save · Esc to cancel</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => { setOpen(false); setText('') }}
            className="p-1 rounded-lg text-text-muted hover:text-cream transition-colors"
          >
            <X size={13} />
          </button>
          <button
            onClick={handleSave}
            disabled={!text.trim()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold
                       transition-all disabled:opacity-40"
            style={{
              background: 'rgba(255,140,0,0.18)',
              border: '1px solid rgba(255,140,0,0.35)',
              color: '#FFA533',
            }}
          >
            <Check size={12} />
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
