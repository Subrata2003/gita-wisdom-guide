/**
 * shareCard.js
 *
 * Renders an off-screen verse card div to a PNG image, then either:
 *  - Triggers native share sheet (Web Share API, works on mobile/Chrome)
 *  - Falls back to direct PNG download on desktop
 */

import { toPng } from 'html-to-image'

/**
 * Main entry point.
 * @param {object} verse  - { chapter, verse, text, sanskrit, theme }
 * @param {string} quote  - Optional highlighted quote (falls back to verse.text)
 */
export async function shareVerseCard(verse, quote) {
  const node = _createCardNode(verse, quote)
  document.body.appendChild(node)

  try {
    // Wait one frame so fonts/layout are applied
    await new Promise(r => requestAnimationFrame(r))
    await new Promise(r => setTimeout(r, 120))

    const dataUrl = await toPng(node, {
      width: 1080,
      height: 1080,
      pixelRatio: 1,
      skipFonts: false,
    })

    document.body.removeChild(node)
    await _share(dataUrl, verse)
  } catch (err) {
    document.body.removeChild(node)
    throw err
  }
}

// ─── Share dispatcher ─────────────────────────────────────────────────────────

async function _share(dataUrl, verse) {
  const title = `Bhagavad Gita · Chapter ${verse.chapter}, Verse ${verse.verse}`
  const text  = verse.text?.slice(0, 140) + '…'

  // Convert dataUrl → Blob → File for Web Share API
  if (navigator.share && navigator.canShare) {
    try {
      const blob = await (await fetch(dataUrl)).blob()
      const file = new File([blob], 'gita-wisdom.png', { type: 'image/png' })
      if (navigator.canShare({ files: [file] })) {
        await navigator.share({ title, text, files: [file] })
        return
      }
    } catch {
      // Web Share failed — fall through to download
    }
  }

  // Desktop fallback: download PNG
  const link    = document.createElement('a')
  link.download = `gita-ch${verse.chapter}-v${verse.verse}.png`
  link.href     = dataUrl
  link.click()
}

// ─── Off-screen card DOM builder ─────────────────────────────────────────────

function _createCardNode(verse, quote) {
  const displayText = quote || verse.text || ''

  const node = document.createElement('div')

  // Absolutely positioned off screen — invisible to user but rendered by browser
  Object.assign(node.style, {
    position:   'fixed',
    top:        '-9999px',
    left:       '-9999px',
    width:      '1080px',
    height:     '1080px',
    zIndex:     '-1',
    overflow:   'hidden',
    fontFamily: '"Inter", "Noto Serif Devanagari", system-ui, sans-serif',
  })

  node.innerHTML = `
    <div style="
      width: 1080px;
      height: 1080px;
      background: linear-gradient(145deg, #0D0B1E 0%, #1A1640 50%, #0D0B1E 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 72px;
      box-sizing: border-box;
      position: relative;
      overflow: hidden;
    ">

      <!-- Decorative outer border -->
      <div style="
        position: absolute; inset: 24px;
        border: 1.5px solid rgba(255,215,0,0.25);
        border-radius: 28px;
        pointer-events: none;
      "></div>

      <!-- Inner glow corners -->
      <div style="
        position: absolute; inset: 0;
        background: radial-gradient(ellipse at 50% 0%, rgba(255,140,0,0.10) 0%, transparent 60%),
                    radial-gradient(ellipse at 50% 100%, rgba(255,215,0,0.07) 0%, transparent 60%);
        pointer-events: none;
      "></div>

      <!-- Mandala watermark -->
      <div style="
        position: absolute;
        width: 600px; height: 600px;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        background: radial-gradient(circle, rgba(255,215,0,0.04) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
      "></div>

      <!-- === CONTENT === -->
      <div style="
        position: relative; z-index: 1;
        display: flex; flex-direction: column;
        align-items: center; gap: 32px;
        width: 100%; max-width: 880px;
        text-align: center;
      ">

        <!-- App logo row -->
        <div style="display:flex; align-items:center; gap:12px;">
          <div style="
            width: 48px; height: 48px;
            background: rgba(255,215,0,0.12);
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
          ">🕉</div>
          <div>
            <div style="font-size:18px; font-weight:700; color:#FFD700; letter-spacing:2px; text-transform:uppercase;">Gita Wisdom Guide</div>
            <div style="font-size:11px; color:rgba(255,215,0,0.5); letter-spacing:3px; text-transform:uppercase; margin-top:2px;">Ancient Wisdom · Modern Life</div>
          </div>
        </div>

        <!-- Saffron line divider -->
        <div style="width:120px; height:2px; background:linear-gradient(90deg, transparent, #FF8C00, #FFD700, #FF8C00, transparent);"></div>

        <!-- Chapter / Verse badge -->
        <div style="
          background: rgba(255,140,0,0.12);
          border: 1px solid rgba(255,140,0,0.35);
          border-radius: 999px;
          padding: 8px 24px;
          font-size: 13px; font-weight: 700;
          color: #FF8C00;
          letter-spacing: 3px;
          text-transform: uppercase;
        ">Chapter ${verse.chapter} · Verse ${verse.verse}</div>

        <!-- Sanskrit Devanagari -->
        ${verse.sanskrit ? `
        <div style="
          background: rgba(255,215,0,0.06);
          border: 1px solid rgba(255,215,0,0.18);
          border-radius: 16px;
          padding: 24px 32px;
          width: 100%;
        ">
          <div style="
            font-family: 'Noto Serif Devanagari', serif;
            font-size: 24px;
            line-height: 1.9;
            letter-spacing: 1px;
            color: #FFD700;
            text-shadow: 0 0 30px rgba(255,215,0,0.4);
          ">${verse.sanskrit}</div>
        </div>` : ''}

        <!-- English translation -->
        <div style="
          font-size: ${displayText.length > 200 ? '20px' : '23px'};
          line-height: 1.7;
          font-style: italic;
          color: #F5E6C8;
          text-shadow: 0 2px 8px rgba(0,0,0,0.6);
          max-width: 820px;
        ">"${displayText}"</div>

        <!-- Saffron line divider -->
        <div style="width:80px; height:1px; background:linear-gradient(90deg, transparent, rgba(255,215,0,0.4), transparent);"></div>

        <!-- Theme + footer -->
        <div style="
          font-size: 12px;
          color: rgba(232,201,122,0.6);
          letter-spacing: 2px;
          text-transform: uppercase;
        ">${verse.theme ? `✦ ${verse.theme}` : '✦ Bhagavad Gita'}</div>

      </div>
    </div>
  `

  return node
}
