/**
 * useJournal — localStorage-backed reflection journal
 *
 * Entry shape:
 * {
 *   id:         string (uuid)
 *   timestamp:  ISO string
 *   reflection: string
 *   source: {
 *     type:      'chat' | 'daily_verse'
 *     query?:    string          // the question asked (chat only)
 *     chapter:   number
 *     verse:     number
 *     verseText: string
 *     sanskrit?: string
 *     theme?:    string
 *   }
 * }
 */

import { useState, useCallback } from 'react'

const KEY = 'gita_journal_v1'

function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]') } catch { return [] }
}

export function useJournal() {
  const [entries, setEntries] = useState(load)

  const _persist = useCallback((next) => {
    localStorage.setItem(KEY, JSON.stringify(next))
    setEntries(next)
  }, [])

  const addEntry = useCallback((reflection, source) => {
    const entry = {
      id:         crypto.randomUUID(),
      timestamp:  new Date().toISOString(),
      reflection: reflection.trim(),
      source,
    }
    _persist([entry, ...load()])   // always read fresh so concurrent saves don't collide
    return entry
  }, [_persist])

  const deleteEntry = useCallback((id) => {
    _persist(load().filter(e => e.id !== id))
  }, [_persist])

  return { entries, addEntry, deleteEntry, total: entries.length }
}
