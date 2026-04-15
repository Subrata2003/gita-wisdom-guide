import { useEffect, useState } from 'react'
import { X, Download, Copy, Check } from 'lucide-react'
import { generateQuoteCard } from '../utils/generateQuoteCard.js'
import { toast } from '../utils/toast.js'

export default function ShareModal({ message, onClose }) {
  const [imgUrl,  setImgUrl]  = useState(null)
  const [copied,  setCopied]  = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const v0 = message.verses?.[0]
    const verseRef = v0
      ? `Bhagavad Gita · Chapter ${v0.chapter}, Verse ${v0.verse}`
      : null

    generateQuoteCard({ text: message.content, verseRef })
      .then((url) => { setImgUrl(url); setLoading(false) })
      .catch(() => setLoading(false))
  }, [message])

  const handleDownload = () => {
    const a    = document.createElement('a')
    a.href     = imgUrl
    a.download = 'gita-wisdom.png'
    a.click()
    toast('Quote card downloaded')
  }

  const handleCopy = async () => {
    try {
      const blob = await fetch(imgUrl).then((r) => r.blob())
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
      setCopied(true)
      setTimeout(() => setCopied(false), 2200)
      toast('Image copied to clipboard')
    } catch {
      // Clipboard API not supported — fall back to download
      handleDownload()
    }
  }

  return (
    /* Backdrop */
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 10000,
        background: 'rgba(0,0,0,0.75)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 20,
        backdropFilter: 'blur(4px)',
      }}
    >
      {/* Card */}
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#14122C',
          border: '1px solid rgba(255,140,0,0.22)',
          borderRadius: 16,
          padding: 24,
          maxWidth: 500,
          width: '100%',
          boxShadow: '0 24px 64px rgba(0,0,0,0.6)',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
          <div>
            <h3 style={{ color: '#FFD700', fontWeight: 700, fontSize: 16, margin: 0 }}>
              Share Wisdom
            </h3>
            <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 12, margin: '3px 0 0' }}>
              Download or copy the quote card
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'rgba(255,255,255,0.45)', padding: 4, lineHeight: 0,
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Preview */}
        <div
          style={{
            background: 'rgba(0,0,0,0.3)',
            borderRadius: 10,
            overflow: 'hidden',
            marginBottom: 16,
            minHeight: 200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {loading ? (
            <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 13 }}>Generating card…</p>
          ) : imgUrl ? (
            <img
              src={imgUrl}
              alt="Quote card preview"
              style={{ width: '100%', display: 'block', borderRadius: 8 }}
            />
          ) : (
            <p style={{ color: 'rgba(255,100,100,0.7)', fontSize: 13 }}>Failed to generate card.</p>
          )}
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={handleDownload}
            disabled={!imgUrl}
            style={{
              flex: 1, padding: '11px 0', borderRadius: 9, cursor: imgUrl ? 'pointer' : 'default',
              background: imgUrl
                ? 'linear-gradient(90deg, #FF8C00, #FFD700)'
                : 'rgba(255,255,255,0.08)',
              color: imgUrl ? '#0D0B1E' : 'rgba(255,255,255,0.3)',
              fontWeight: 700, fontSize: 14, border: 'none',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              transition: 'opacity 0.2s',
            }}
          >
            <Download size={15} /> Download PNG
          </button>

          <button
            onClick={handleCopy}
            disabled={!imgUrl}
            style={{
              flex: 1, padding: '11px 0', borderRadius: 9, cursor: imgUrl ? 'pointer' : 'default',
              background: 'rgba(255,255,255,0.07)',
              border: '1px solid rgba(255,255,255,0.14)',
              color: copied ? '#FFD700' : 'rgba(255,255,255,0.75)',
              fontWeight: 600, fontSize: 14,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              transition: 'color 0.2s',
            }}
          >
            {copied
              ? <><Check size={15} /> Copied!</>
              : <><Copy size={15} /> Copy Image</>
            }
          </button>
        </div>
      </div>
    </div>
  )
}
