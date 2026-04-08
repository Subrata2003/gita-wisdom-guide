/**
 * Generates 3 contextual follow-up questions from a completed Krishna response.
 * Pure frontend — no LLM call, no token cost.
 * Uses themes, mood, and verse reference to pick relevant questions.
 */

const THEME_QUESTIONS = {
  duty:            ['How do I identify my true duty when roles conflict?', 'What happens when fulfilling duty causes pain to others?'],
  dharma:          ['How does my dharma change across different stages of life?', 'Can dharma differ from person to person?'],
  detachment:      ['How do I practice detachment without becoming cold or indifferent?', 'What is the difference between detachment and not caring?'],
  karma:           ['How does my past karma shape my present situation?', 'Can sincere action today change the effects of past karma?'],
  meditation:      ['What meditation practice does the Gita recommend for a restless mind?', 'How long should I meditate daily according to Krishna?'],
  yoga:            ['Which path of yoga — karma, jnana, or bhakti — is right for me?', 'How does the Gita define yoga differently from modern fitness?'],
  'self-realization': ['What are the signs that one is moving toward self-realization?', 'How do I begin the journey of knowing my true self?'],
  surrender:       ['What does surrendering to the divine truly mean in practice?', 'How do I surrender without feeling powerless?'],
  equanimity:      ['How do I stay balanced when circumstances swing between joy and sorrow?', 'Which Gita practice builds equanimity most effectively?'],
  action:          ['How do I act wholeheartedly without being attached to the outcome?', 'What distinguishes right action from wrong action in the Gita?'],
  mind:            ['How do I tame a restless, distracted mind?', 'What does Krishna say is the greatest enemy within us?'],
  devotion:        ['How can I deepen my devotion as part of everyday life?', 'Does the Gita say devotion is only for religious or spiritual people?'],
  knowledge:       ['Where does the Gita say true wisdom begins?', 'How is self-knowledge different from intellectual knowledge?'],
  renunciation:    ['Does renunciation mean giving up everything external?', 'Can a householder — with family and work — practice true renunciation?'],
  fear:            ['What does Krishna say is the root cause of all fear?', 'How do I face uncertainty with courage according to the Gita?'],
  grief:           ['How do I honor grief while still fulfilling my responsibilities?', 'What does Krishna teach about the eternal nature of the soul?'],
  peace:           ['What are the concrete steps toward lasting inner peace in the Gita?', 'Why do I still feel restless even after spiritual practice?'],
  wisdom:          ['How do I cultivate the stillness that allows wisdom to arise?', 'What does the Gita say about the relationship between wisdom and action?'],
  liberation:      ['What does liberation (moksha) mean in everyday terms?', 'Does the Gita say liberation is possible while still living in the world?'],
  soul:            ['How does understanding the soul change the way I face difficulties?', 'What is the difference between the soul and the ego?'],
}

const MOOD_QUESTIONS = {
  grief:     ['How do I find meaning when something precious is lost?', 'What verse from the Gita brings the most comfort in times of sorrow?'],
  anger:     ['How do I transform anger into something constructive?', 'Why does Krishna warn so strongly against unchecked anger?'],
  anxiety:   ['What specific daily practice calms a worried mind according to the Gita?', 'How do I stop my thoughts from spiraling into worst-case scenarios?'],
  confusion: ['What is the first step the Gita recommends when I feel completely lost?', 'How did Arjuna move from confusion to clarity on the battlefield?'],
  despair:   ['How do I find hope when every path seems closed?', 'Did Arjuna ever feel this level of despair, and how did he recover?'],
  longing:   ['How do I find a fulfillment that does not fade with time?', 'What does the Gita say about the nature of desire and longing?'],
  curiosity: ['Which chapter of the Gita explores this idea most deeply?', 'What is the philosophical foundation behind this teaching?'],
}

const GENERIC_QUESTIONS = [
  'How can I apply this teaching in a small, practical way today?',
  'Which single verse from the Gita captures this wisdom most powerfully?',
  'What would Krishna advise someone who is just beginning this practice?',
  'How did Arjuna receive this teaching — did he understand it immediately?',
  'What is one habit I could build to live this teaching every day?',
  'Are there other parts of the Gita that speak to this same theme?',
  'How does this wisdom apply when life feels overwhelming and chaotic?',
]

function pick(arr, index) {
  return arr[index % arr.length]
}

export function generateFollowUps(message) {
  const themes = message.themes || []
  const mood   = message.mood   || 'neutral'
  const verse  = message.verses?.[0]

  const results = []

  // 1. Theme-based question — from the first matched theme
  for (const theme of themes) {
    const key = theme.toLowerCase().replace(/[^a-z-]/g, '')
    if (THEME_QUESTIONS[key]) {
      // pick second question if we already have something similar, for variety
      results.push(THEME_QUESTIONS[key][results.length % 2])
      break
    }
  }

  // 2. Mood-based question — only for non-neutral moods
  if (mood && mood !== 'neutral' && MOOD_QUESTIONS[mood]) {
    results.push(MOOD_QUESTIONS[mood][0])
  }

  // 3. Verse-specific question — if a verse was cited
  if (verse && results.length < 3) {
    results.push(
      `Can you explain Chapter ${verse.chapter}, Verse ${verse.verse} in simpler words and how I can live it?`
    )
  }

  // 4. Fill remaining slots with generic questions (avoiding duplicates)
  let genericIdx = 0
  while (results.length < 3) {
    const q = GENERIC_QUESTIONS[genericIdx % GENERIC_QUESTIONS.length]
    if (!results.includes(q)) results.push(q)
    genericIdx++
  }

  return results.slice(0, 3)
}
