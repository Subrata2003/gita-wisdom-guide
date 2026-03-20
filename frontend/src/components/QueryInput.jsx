import { useState, useRef, useCallback } from 'react'
import { Send } from 'lucide-react'

export default function QueryInput({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('')
  const textareaRef = useRef(null)

  const submit = useCallback(() => {
    const trimmed = query.trim()
    if (!trimmed || isLoading) return
    onSubmit(trimmed)
    setQuery('')
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }, [query, isLoading, onSubmit])

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        submit()
      }
    },
    [submit]
  )

  const handleChange = useCallback((e) => {
    setQuery(e.target.value)
    // Auto-resize
    const el = e.target
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 160) + 'px'
  }, [])

  const canSubmit = query.trim().length > 0 && !isLoading

  return (
    <div className="flex items-end gap-3">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask for guidance… e.g. 'I'm overwhelmed by a difficult decision'"
          rows={1}
          disabled={isLoading}
          className="input-base w-full pr-4 text-sm leading-relaxed"
          style={{ minHeight: '52px', maxHeight: '160px' }}
        />
        <div className="absolute right-3 bottom-3 text-[10px] text-text-muted select-none">
          ⏎ Enter
        </div>
      </div>

      <button
        onClick={submit}
        disabled={!canSubmit}
        aria-label="Send"
        className="w-12 h-12 rounded-xl flex-shrink-0 flex items-center justify-center
                   bg-gradient-to-br from-saffron to-gold text-midnight
                   hover:shadow-saffron hover:scale-105 active:scale-95
                   disabled:opacity-40 disabled:hover:scale-100 disabled:hover:shadow-none
                   transition-all duration-200"
      >
        <Send size={18} />
      </button>
    </div>
  )
}
