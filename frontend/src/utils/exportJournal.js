/**
 * exportJournalToPDF — exports all journal entries to a formatted A4 PDF.
 *
 * Uses jsPDF for text-based (searchable) PDF generation.
 * Devanagari Sanskrit is skipped because jsPDF's built-in fonts don't support it.
 */

import jsPDF from 'jspdf'

const PAGE_W  = 210
const PAGE_H  = 297
const MARGIN  = 18
const CONTENT_W = PAGE_W - MARGIN * 2

// ── Colour palette (RGB arrays) ──────────────────────────────────────────────
const C = {
  navyDark:   [14, 12, 40],
  navyMid:    [26, 22, 64],
  gold:       [255, 215, 0],
  saffron:    [255, 140, 0],
  amber:      [200, 168, 75],
  muted:      [123, 111, 160],
  dimMuted:   [90, 80, 120],
  ink:        [30, 24, 70],
  verseText:  [80, 65, 40],
  separator:  [210, 200, 235],
  ruleGold:   [200, 168, 75],
}

function setColor(doc, rgb) {
  doc.setTextColor(...rgb)
}

function setDraw(doc, rgb) {
  doc.setDrawColor(...rgb)
}

function setFill(doc, rgb) {
  doc.setFillColor(...rgb)
}

/**
 * Add a block of wrapped text, advancing `y`. Returns new `y`.
 * Automatically adds a new page if the block won't fit.
 */
function addWrapped(doc, text, x, yRef, opts) {
  const { size = 10, font = 'normal', color = C.ink, maxW = CONTENT_W, lineGap = 1.5 } = opts
  doc.setFontSize(size)
  doc.setFont('helvetica', font)
  setColor(doc, color)
  const lines = doc.splitTextToSize(text, maxW)
  const lineH = size * 0.3528 * lineGap      // pt → mm
  if (yRef[0] + lines.length * lineH + 4 > PAGE_H - MARGIN) {
    doc.addPage()
    yRef[0] = MARGIN
  }
  doc.text(lines, x, yRef[0])
  yRef[0] += lines.length * lineH
  return yRef[0]
}

function ensureSpace(doc, yRef, needed = 20) {
  if (yRef[0] + needed > PAGE_H - MARGIN) {
    doc.addPage()
    yRef[0] = MARGIN
  }
}

function formatDateLong(iso) {
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

export function exportJournalToPDF(entries) {
  if (!entries || entries.length === 0) return

  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })

  // ── Cover header block ─────────────────────────────────────────────────────
  setFill(doc, C.navyDark)
  doc.rect(0, 0, PAGE_W, 44, 'F')

  // Saffron accent line at very top
  setFill(doc, C.saffron)
  doc.rect(0, 0, PAGE_W, 2, 'F')

  // Gold left accent bar
  setFill(doc, C.gold)
  doc.rect(MARGIN, 10, 2, 26, 'F')

  // App title
  doc.setFontSize(20)
  doc.setFont('helvetica', 'bold')
  setColor(doc, C.gold)
  doc.text('Gita Wisdom Guide', MARGIN + 8, 21)

  // Subtitle
  doc.setFontSize(11)
  doc.setFont('helvetica', 'normal')
  setColor(doc, C.amber)
  doc.text('Personal Reflection Journal', MARGIN + 8, 30)

  // Export meta
  doc.setFontSize(8)
  setColor(doc, C.muted)
  const exportDate = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })
  doc.text(
    `Exported on ${exportDate}  ·  ${entries.length} reflection${entries.length !== 1 ? 's' : ''}`,
    MARGIN + 8,
    38,
  )

  // ── Body ──────────────────────────────────────────────────────────────────
  const yRef = [52]   // mutable y cursor passed by reference

  const groups = groupByDate(entries)

  for (const [, dateEntries] of Object.entries(groups)) {
    const dateLabel = formatDateLong(dateEntries[0].timestamp).toUpperCase()

    // Date section header with gold rule
    ensureSpace(doc, yRef, 18)
    setDraw(doc, C.ruleGold)
    doc.setLineWidth(0.3)
    doc.line(MARGIN, yRef[0], PAGE_W - MARGIN, yRef[0])
    yRef[0] += 5

    doc.setFontSize(9)
    doc.setFont('helvetica', 'bold')
    setColor(doc, C.amber)
    doc.text(dateLabel, MARGIN, yRef[0])
    yRef[0] += 8

    for (const entry of dateEntries) {
      const s = entry.source
      ensureSpace(doc, yRef, 35)

      // ── Entry: badge row ──────────────────────────────────────────────────
      doc.setFontSize(8)
      doc.setFont('helvetica', 'bold')
      setColor(doc, C.saffron)
      const badge = `Ch ${s.chapter ?? '?'} · V ${s.verse ?? '?'}`
      doc.text(badge, MARGIN, yRef[0])

      let xCursor = MARGIN + doc.getTextWidth(badge) + 5

      doc.setFont('helvetica', 'normal')
      setColor(doc, C.muted)
      const srcLabel = s.type === 'daily_verse' ? '✦ Daily Verse' : '✦ Conversation'
      doc.text(srcLabel, xCursor, yRef[0])
      xCursor += doc.getTextWidth(srcLabel) + 5

      if (s.theme) {
        setColor(doc, C.amber)
        doc.text(s.theme, xCursor, yRef[0])
      }

      // Time aligned right
      const timeStr = formatTime(entry.timestamp)
      setColor(doc, C.dimMuted)
      doc.text(timeStr, PAGE_W - MARGIN - doc.getTextWidth(timeStr), yRef[0])

      yRef[0] += 6

      // ── Entry: reflection text ────────────────────────────────────────────
      addWrapped(doc, entry.reflection, MARGIN, yRef, {
        size: 11, font: 'normal', color: C.ink, lineGap: 1.5,
      })
      yRef[0] += 3

      // ── Entry: verse text (English) ───────────────────────────────────────
      if (s.verseText) {
        addWrapped(doc, `"${s.verseText}"`, MARGIN + 4, yRef, {
          size: 9, font: 'italic', color: C.verseText, maxW: CONTENT_W - 8, lineGap: 1.45,
        })
        yRef[0] += 1
        doc.setFontSize(8)
        doc.setFont('helvetica', 'normal')
        setColor(doc, C.amber)
        doc.text(`— Bhagavad Gita, Chapter ${s.chapter}, Verse ${s.verse}`, MARGIN + 4, yRef[0])
        yRef[0] += 5
      }

      // ── Entry: original question (chat only) ──────────────────────────────
      if (s.query) {
        addWrapped(doc, `Question: "${s.query}"`, MARGIN + 2, yRef, {
          size: 9, font: 'italic', color: C.dimMuted, maxW: CONTENT_W - 4, lineGap: 1.4,
        })
        yRef[0] += 2
      }

      // ── Entry separator ───────────────────────────────────────────────────
      yRef[0] += 3
      setDraw(doc, C.separator)
      doc.setLineWidth(0.2)
      doc.line(MARGIN, yRef[0], PAGE_W - MARGIN, yRef[0])
      yRef[0] += 7
    }

    yRef[0] += 4
  }

  // ── Footer on every page ──────────────────────────────────────────────────
  const totalPages = doc.internal.getNumberOfPages()
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i)
    doc.setFontSize(7.5)
    doc.setFont('helvetica', 'normal')
    setColor(doc, C.dimMuted)
    doc.text('Gita Wisdom Guide — Personal Reflection Journal', MARGIN, PAGE_H - 8)
    const pageStr = `${i} / ${totalPages}`
    doc.text(pageStr, PAGE_W - MARGIN - doc.getTextWidth(pageStr), PAGE_H - 8)
  }

  // ── Save ──────────────────────────────────────────────────────────────────
  const today = new Date().toISOString().slice(0, 10)
  doc.save(`gita-journal-${today}.pdf`)
}
