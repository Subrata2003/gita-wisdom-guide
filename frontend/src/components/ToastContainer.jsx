import { useEffect, useState } from 'react'
import { Check, AlertCircle, Info } from 'lucide-react'

const ICONS = {
  success: <Check size={13} />,
  error:   <AlertCircle size={13} />,
  info:    <Info size={13} />,
}

const COLORS = {
  success: { border: 'rgba(255,140,0,0.35)', icon: '#FFD700',  text: 'rgba(255,240,200,0.95)' },
  error:   { border: 'rgba(248,113,113,0.4)', icon: '#f87171', text: 'rgba(255,220,220,0.95)' },
  info:    { border: 'rgba(147,197,253,0.35)', icon: '#93c5fd', text: 'rgba(210,235,255,0.95)' },
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    function handler(e) {
      const { id, message, type = 'success' } = e.detail
      setToasts(prev => [...prev, { id, message, type, visible: true }])

      // Start fade-out after 2.2s, remove after 2.9s
      setTimeout(() => {
        setToasts(prev => prev.map(t => t.id === id ? { ...t, visible: false } : t))
      }, 2200)
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id))
      }, 2900)
    }

    window.addEventListener('app:toast', handler)
    return () => window.removeEventListener('app:toast', handler)
  }, [])

  if (toasts.length === 0) return null

  return (
    <div style={{
      position: 'fixed',
      bottom: 28,
      right: 24,
      zIndex: 99999,
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
      pointerEvents: 'none',
    }}>
      {toasts.map(({ id, message, type, visible }) => {
        const c = COLORS[type] || COLORS.success
        return (
          <div
            key={id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 9,
              padding: '10px 16px',
              borderRadius: 10,
              background: 'rgba(13,11,30,0.96)',
              border: `1px solid ${c.border}`,
              boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
              backdropFilter: 'blur(8px)',
              color: c.text,
              fontSize: 13,
              fontWeight: 500,
              maxWidth: 300,
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateX(0)' : 'translateX(16px)',
              transition: 'opacity 0.4s ease, transform 0.4s ease',
            }}
          >
            <span style={{ color: c.icon, flexShrink: 0 }}>{ICONS[type]}</span>
            {message}
          </div>
        )
      })}
    </div>
  )
}
