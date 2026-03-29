/**
 * WakeUpScreen — shown while the Render backend is waking from sleep.
 *
 * Polls GET /api/health every 3 seconds.
 * Once the backend responds, calls onReady() to fade into the main app.
 */

import { useEffect, useRef, useState } from 'react'
import { getHealth } from '../services/api.js'

const MESSAGES = [
  'Awakening Krishna\'s wisdom…',
  'Lighting the sacred lamp…',
  'Opening the Bhagavad Gita…',
  'Summoning ancient teachings…',
  'Preparing the divine chariot…',
]

export default function WakeUpScreen({ onReady }) {
  const [seconds,  setSeconds]  = useState(0)
  const [msgIndex, setMsgIndex] = useState(0)
  const [fading,   setFading]   = useState(false)
  const onReadyRef = useRef(onReady)
  useEffect(() => { onReadyRef.current = onReady }, [onReady])

  // Rotate messages every 4 seconds
  useEffect(() => {
    const t = setInterval(() => setMsgIndex(i => (i + 1) % MESSAGES.length), 4000)
    return () => clearInterval(t)
  }, [])

  // Count seconds elapsed
  useEffect(() => {
    const t = setInterval(() => setSeconds(s => s + 1), 1000)
    return () => clearInterval(t)
  }, [])

  // Poll health every 3 seconds
  useEffect(() => {
    let stopped = false

    async function poll() {
      while (!stopped) {
        try {
          await getHealth()
          if (!stopped) {
            setFading(true)
            setTimeout(() => onReadyRef.current(), 700)   // wait for fade-out animation
          }
          return
        } catch {
          // backend still sleeping — wait 3s and try again
          await new Promise(r => setTimeout(r, 3000))
        }
      }
    }

    poll()
    return () => { stopped = true }
  }, [])  // intentionally empty — onReady is accessed via ref to avoid restart loop

  return (
    <div
      style={{
        position:   'fixed', inset: 0, zIndex: 9999,
        display:    'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        background: 'linear-gradient(135deg, #0D0B1E 0%, #14122C 60%, #1A1640 100%)',
        transition: 'opacity 0.7s ease',
        opacity:    fading ? 0 : 1,
      }}
    >
      {/* Background glow */}
      <div style={{
        position: 'absolute', width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255,140,0,0.06) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Om logo — floats gently */}
      <div style={{ animation: 'float 3s ease-in-out infinite', marginBottom: 32 }}>
        <img
          src="/images/hero-om-V2.png"
          alt="Om"
          style={{ width: 110, height: 110, objectFit: 'contain', opacity: 0.92 }}
        />
      </div>

      {/* App name */}
      <h1 style={{
        fontSize: 26, fontWeight: 700, letterSpacing: '0.04em', marginBottom: 6,
        background: 'linear-gradient(90deg, #FF8C00, #FFD700, #FF8C00)',
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
      }}>
        Gita Wisdom Guide
      </h1>

      <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.35)', marginBottom: 40, letterSpacing: '0.08em' }}>
        DIVINE KNOWLEDGE · TIMELESS GUIDANCE
      </p>

      {/* Rotating message */}
      <p style={{
        fontSize: 15, color: 'rgba(255,215,0,0.75)', marginBottom: 28,
        minHeight: 24, textAlign: 'center',
        transition: 'opacity 0.4s',
      }}>
        {MESSAGES[msgIndex]}
      </p>

      {/* Animated dots */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 36 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 8, height: 8, borderRadius: '50%',
            background: '#FF8C00',
            animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
          }} />
        ))}
      </div>

      {/* Elapsed time hint — only show after 5 seconds */}
      {seconds >= 5 && (
        <p style={{
          fontSize: 12, color: 'rgba(255,255,255,0.22)',
          textAlign: 'center', maxWidth: 260, lineHeight: 1.6,
        }}>
          The server is waking up from sleep.
          <br />This takes up to 30 seconds on first visit.
        </p>
      )}

      {/* Elapsed seconds — subtle */}
      {seconds >= 5 && (
        <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.15)', marginTop: 8 }}>
          {seconds}s
        </p>
      )}
    </div>
  )
}
