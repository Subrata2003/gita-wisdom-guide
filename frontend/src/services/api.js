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
