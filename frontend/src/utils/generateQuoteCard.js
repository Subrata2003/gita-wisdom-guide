/**
 * Generates a 1080×1080 quote card PNG (data URL) from a Krishna response.
 * Pure Canvas API — no external dependencies.
 */

const W = 1080
const H = 1080

function loadImg(src) {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload  = () => resolve(img)
    img.onerror = () => resolve(null)   // skip gracefully if image fails
    img.src = src
  })
}

function stripMarkdown(text) {
  return text
    .replace(/#{1,6}\s+/g, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`(.+?)`/g, '$1')
    .replace(/\[(.+?)\]\(.+?\)/g, '$1')
    .replace(/\n+/g, ' ')
    .trim()
}

/** Wraps text in a canvas context. Returns the Y of the last line drawn. */
function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(' ')
  let line = ''
  let curY  = y
  for (let i = 0; i < words.length; i++) {
    const test = line + words[i] + ' '
    if (ctx.measureText(test).width > maxWidth && i > 0) {
      ctx.fillText(line.trim(), x, curY)
      line = words[i] + ' '
      curY += lineHeight
    } else {
      line = test
    }
  }
  ctx.fillText(line.trim(), x, curY)
  return curY
}

export async function generateQuoteCard({ text, verseRef }) {
  const canvas  = document.createElement('canvas')
  canvas.width  = W
  canvas.height = H
  const ctx     = canvas.getContext('2d')

  // ── Background ────────────────────────────────────────────────
  const bg = ctx.createLinearGradient(0, 0, W, H)
  bg.addColorStop(0,   '#0D0B1E')
  bg.addColorStop(0.6, '#14122C')
  bg.addColorStop(1,   '#1A1640')
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, W, H)

  // Soft centre glow
  const glow = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, 480)
  glow.addColorStop(0, 'rgba(255,140,0,0.07)')
  glow.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = glow
  ctx.fillRect(0, 0, W, H)

  // ── Om logo ───────────────────────────────────────────────────
  const omImg = await loadImg('/images/hero-om-V2.png')
  if (omImg) ctx.drawImage(omImg, W / 2 - 55, 72, 110, 110)

  // ── App title ─────────────────────────────────────────────────
  ctx.textAlign    = 'center'
  ctx.textBaseline = 'alphabetic'

  ctx.font      = 'bold 38px Georgia, serif'
  ctx.fillStyle = '#FFD700'
  ctx.fillText('Gita Wisdom Guide', W / 2, 238)

  ctx.font      = '17px sans-serif'
  ctx.fillStyle = 'rgba(255,255,255,0.28)'
  ctx.fillText('DIVINE KNOWLEDGE  ·  TIMELESS GUIDANCE', W / 2, 268)

  // ── Top divider ───────────────────────────────────────────────
  const divGrad = () => {
    const g = ctx.createLinearGradient(110, 0, W - 110, 0)
    g.addColorStop(0,   'rgba(255,140,0,0)')
    g.addColorStop(0.5, 'rgba(255,140,0,0.55)')
    g.addColorStop(1,   'rgba(255,140,0,0)')
    return g
  }
  ctx.strokeStyle = divGrad()
  ctx.lineWidth   = 1.5
  ctx.beginPath()
  ctx.moveTo(110, 294)
  ctx.lineTo(W - 110, 294)
  ctx.stroke()

  // ── Decorative quote mark ─────────────────────────────────────
  ctx.font      = 'bold 130px Georgia, serif'
  ctx.fillStyle = 'rgba(255,140,0,0.18)'
  ctx.textAlign = 'left'
  ctx.fillText('\u201C', 76, 430)

  // ── Quote text ────────────────────────────────────────────────
  const raw       = stripMarkdown(text)
  const maxChars  = 340
  const truncated = raw.length > maxChars
    ? raw.slice(0, maxChars).replace(/\s+\S*$/, '') + '\u2026'
    : raw

  ctx.font      = '29px Georgia, serif'
  ctx.fillStyle = 'rgba(255,245,220,0.90)'
  ctx.textAlign = 'center'
  const lastY   = wrapText(ctx, truncated, W / 2, 360, W - 220, 48)

  // ── Verse reference ───────────────────────────────────────────
  let afterQuoteY = lastY + 60
  if (verseRef) {
    ctx.font      = 'italic 23px Georgia, serif'
    ctx.fillStyle = 'rgba(255,215,0,0.65)'
    ctx.textAlign = 'center'
    ctx.fillText(`\u2014 ${verseRef}`, W / 2, afterQuoteY)
    afterQuoteY  += 44
  }

  // ── Bottom divider ────────────────────────────────────────────
  const bottomDivY = Math.max(afterQuoteY + 30, H - 100)
  ctx.strokeStyle = divGrad()
  ctx.lineWidth   = 1.5
  ctx.beginPath()
  ctx.moveTo(110, bottomDivY)
  ctx.lineTo(W - 110, bottomDivY)
  ctx.stroke()

  // ── Footer ────────────────────────────────────────────────────
  ctx.font      = '18px sans-serif'
  ctx.fillStyle = 'rgba(255,255,255,0.20)'
  ctx.textAlign = 'center'
  ctx.fillText('gita-wisdom-guide.vercel.app', W / 2, bottomDivY + 38)

  return canvas.toDataURL('image/png')
}
