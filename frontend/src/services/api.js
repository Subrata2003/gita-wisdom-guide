import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60s — LLM can be slow
})

// Intercept errors for cleaner handling
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Network error'
    return Promise.reject(new Error(message))
  }
)

export const getWisdom = async (query, sessionId = null) => {
  const { data } = await api.post('/query', {
    query,
    session_id: sessionId || undefined,
  })
  return data
}

export const getHealth = async () => {
  const { data } = await api.get('/health')
  return data
}

export const getThemes = async () => {
  const { data } = await api.get('/themes')
  return data
}

export const searchVerses = async ({ q, theme, chapter, limit = 10 }) => {
  const params = new URLSearchParams()
  if (q) params.append('q', q)
  if (theme) params.append('theme', theme)
  if (chapter) params.append('chapter', chapter)
  params.append('limit', String(limit))
  const { data } = await api.get(`/verses/search?${params.toString()}`)
  return data
}

export const getSessionHistory = async (sessionId) => {
  const { data } = await api.get(`/session/${sessionId}/history`)
  return data
}

export const clearSession = async (sessionId) => {
  await api.delete(`/session/${sessionId}`)
}

/**
 * Stream a wisdom query via Server-Sent Events.
 *
 * callbacks:
 *   onToken(text)  — called for each streamed chunk
 *   onDone(event)  — called with { verses, themes, session_id } when complete
 *   onError(err)   — called on network or server error
 *
 * Returns { abort } — call abort() to cancel mid-stream.
 */
export function streamWisdom(query, sessionId, { onToken, onDone, onError }) {
  const controller = new AbortController()

  fetch('/api/query/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId || undefined }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`Server error ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        // SSE lines end with \n\n — process complete events
        const parts = buffer.split('\n\n')
        buffer = parts.pop()           // keep trailing incomplete chunk

        for (const part of parts) {
          const line = part.trim()
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === 'token') onToken(event.content)
            else if (event.type === 'done')  onDone(event)
            else if (event.type === 'error') onError(new Error(event.message))
          } catch {
            // ignore malformed SSE line
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(err)
    })

  return { abort: () => controller.abort() }
}
