import streamlit as st

st.set_page_config(
    page_title="Gita Wisdom Guide",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import json
import google.generativeai as genai
import re
from typing import List, Dict, Optional

# Custom CSS for better styling
st.markdown("""
<style>
.stButton > button {
    width: 100%;
    border-radius: 20px;
}
.main .block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #ff6b35; font-size: 3rem; margin-bottom: 0;">🕉️ Gita Wisdom Guide</h1>
    <p style="font-size: 1.2rem; color: #666; margin-top: 0;">
        Discover timeless wisdom from the Bhagavad Gita for modern life challenges
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

class GitaRetriever:
    def __init__(self, verses_data):
        self.verses_data = verses_data
        
        # Topic-theme mapping
        self.topic_themes = {
            'stress': ['peace', 'meditation', 'detachment'],
            'depression': ['peace', 'knowledge', 'soul'],
            'anxiety': ['peace', 'meditation', 'detachment'],
            'fear': ['peace', 'knowledge', 'soul'],
            'anger': ['peace', 'detachment', 'duty'],
            'confusion': ['knowledge', 'duty', 'action'],
            'purpose': ['duty', 'action', 'devotion'],
            'death': ['soul', 'knowledge', 'detachment'],
            'suffering': ['peace', 'detachment', 'knowledge'],
            'relationships': ['detachment', 'devotion', 'duty'],
            'work': ['action', 'duty', 'detachment'],
            'success': ['action', 'detachment', 'duty'],
            'failure': ['peace', 'detachment', 'action']
        }
    
    def extract_theme(self, text: str) -> str:
        """Extract basic theme from verse content"""
        text_lower = text.lower()
        
        themes = {
            'duty': ['duty', 'dharma', 'righteous', 'obligation'],
            'detachment': ['attachment', 'detachment', 'renunciation', 'surrender'],
            'knowledge': ['knowledge', 'wisdom', 'understand', 'realize'],
            'devotion': ['devotion', 'worship', 'love', 'surrender'],
            'action': ['action', 'work', 'perform', 'activity'],
            'soul': ['soul', 'self', 'atman', 'eternal'],
            'peace': ['peace', 'tranquil', 'calm', 'serenity'],
            'meditation': ['meditation', 'yoga', 'mind', 'concentration']
        }
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
        
        return 'general'
    
    def extract_query_themes(self, query: str) -> List[str]:
        """Extract relevant themes from the query"""
        query_lower = query.lower()
        relevant_themes = []
        
        for topic, themes in self.topic_themes.items():
            if topic in query_lower:
                relevant_themes.extend(themes)
        
        return list(dict.fromkeys(relevant_themes)) if relevant_themes else ['general']
    
    def find_relevant_verses(self, query: str, max_results: int = 5) -> List[Dict]:
        """Find relevant verses with theme matching and keyword search"""
        query_lower = query.lower()
        themes = self.extract_query_themes(query)
        
        scored_verses = []
        
        for verse in self.verses_data:
            score = 0
            verse_text_lower = verse['text'].lower()
            verse_theme = self.extract_theme(verse['text'])
            
            # Theme matching
            if verse_theme in themes:
                score += 3
            
            # Direct keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 3 and word in verse_text_lower:
                    score += 2
            
            # Contextual keyword matching
            context_keywords = {
                'stress': ['mind', 'peace', 'calm', 'worry', 'anxiety'],
                'work': ['duty', 'action', 'karma', 'perform'],
                'failure': ['result', 'attachment', 'success', 'defeat'],
                'purpose': ['dharma', 'path', 'goal', 'destiny'],
                'relationships': ['love', 'attachment', 'others', 'devotion']
            }
            
            for topic, keywords in context_keywords.items():
                if topic in query_lower:
                    for keyword in keywords:
                        if keyword in verse_text_lower:
                            score += 1
            
            if score > 0:
                verse_copy = verse.copy()
                verse_copy['relevance_score'] = score
                verse_copy['theme'] = verse_theme
                scored_verses.append(verse_copy)
        
        # Sort by relevance
        scored_verses.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_verses[:max_results]

class GitaLLMHandler:
    def __init__(self):
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
    
    def generate_response(self, query: str, context: Dict) -> Dict:
        """Generate response using the LLM"""
        if not self.model:
            return {
                'response': "API service not properly configured. Please check your API keys.",
                'error': True
            }
        
        try:
            verses_text = context.get('formatted_context', '')
            themes = context.get('query_themes', [])
            
            system_prompt = """You are a wise guide inspired by the teachings of Krishna in the Bhagavad Gita. Your responses should:

1. Be compassionate, wise, and gentle
2. Draw from the philosophical teachings of the Gita
3. Speak with the wisdom and authority of a spiritual teacher
4. Use inclusive language that helps seekers of all backgrounds
5. Provide practical guidance rooted in spiritual wisdom
6. Always reference the relevant verses when possible
7. Acknowledge human struggles with empathy
8. Guide towards dharma (righteous action) and inner peace

For serious mental health concerns, acknowledge the wisdom while also suggesting professional support."""

            prompt = f"""{system_prompt}

User's Question: "{query}"

Relevant Bhagavad Gita Verses:
{verses_text}

Key Themes Identified: {', '.join(themes)}

Based on these sacred teachings, provide a response that:
1. Addresses the user's concern with compassion
2. References the relevant verses naturally
3. Provides actionable spiritual guidance
4. Maintains the wisdom and tone of a spiritual teacher"""

            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Add mental health disclaimer if needed
            if self._needs_mental_health_disclaimer(query):
                response_text += "\n\n*Note: While spiritual wisdom provides great comfort, if you're experiencing persistent distress, please also consider speaking with a mental health professional or counselor.*"
            
            return {
                'response': response_text,
                'used_verses': context.get('used_verses', []),
                'themes': context.get('query_themes', []),
                'error': False
            }
            
        except Exception as e:
            return {
                'response': f"I encountered a difficulty in providing guidance: {str(e)}",
                'error': True
            }
    
    def _needs_mental_health_disclaimer(self, query: str) -> bool:
        """Check if query indicates serious mental health concerns"""
        serious_keywords = [
            'suicide', 'kill myself', 'end my life', 'depression', 
            'severely depressed', 'hopeless', 'can\'t go on',
            'worthless', 'want to die', 'self harm'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in serious_keywords)

# Load verses data
@st.cache_data
def load_verses():
    try:
        with open('data/reformatted_bhagavad_gita.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

verses = load_verses()

# Initialize components
if verses:
    retriever = GitaRetriever(verses)
    llm_handler = GitaLLMHandler()
    
    # Sidebar
    with st.sidebar:
        st.header("📚 About")
        st.markdown("""
        This guide draws wisdom from the **Bhagavad Gita** to help you navigate life's challenges with spiritual insight.
        
        **How it works:**
        1. Ask any question about life, work, relationships, or spirituality
        2. The system finds relevant verses from the Gita
        3. Receive guidance inspired by Krishna's teachings
        """)
        
        st.header("📊 Database Info")
        st.metric("Total Verses", len(verses))
        st.metric("Chapters", "18")
        
        st.header("🎯 Example Questions")
        st.markdown("""
        - "I'm feeling stressed at work"
        - "How do I deal with failure?"
        - "What is my purpose in life?"
        - "How to handle difficult relationships?"
        - "I'm afraid of making decisions"
        """)
        
        st.header("⚠️ Disclaimer")
        st.markdown("""
        This tool provides spiritual guidance based on the Bhagavad Gita. 
        For serious mental health concerns, please consult a qualified professional.
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <p style="color: #666; font-size: 0.9rem;">
                Made with ❤️ by <strong>Subrata</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["💬 Ask Question", "🎯 Sample Queries"])
    
    with tab1:
        st.markdown("### 💬 Ask Your Question")
        
        # Query input
        query = st.text_area(
            "What guidance do you seek?",
            value=st.session_state.current_query,
            placeholder="Type your question here... (e.g., 'I'm feeling overwhelmed at work')",
            height=100
        )
        
        # Submit and clear buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submit_button = st.button("🔮 Get Guidance", type="primary")
        with col2:
            if st.button("🧹 Clear"):
                st.session_state.current_query = ""
                st.rerun()
        
        # Process query
        if submit_button and query.strip():
            with st.spinner("🔍 Searching for relevant wisdom..."):
                # Find relevant verses
                relevant_verses = retriever.find_relevant_verses(query)
                themes = retriever.extract_query_themes(query)
                
                # Create context
                context_parts = []
                for verse in relevant_verses:
                    verse_text = f"Chapter {verse['chapter']}, Verse {verse['verse']}: {verse['text']}"
                    context_parts.append(verse_text)
                
                context = {
                    'formatted_context': '\n\n'.join(context_parts),
                    'used_verses': relevant_verses,
                    'query_themes': themes,
                    'total_verses': len(relevant_verses)
                }
            
            with st.spinner("💭 Generating guidance..."):
                # Generate response
                result = llm_handler.generate_response(query, context)
            
            # Display response
            if not result.get('error'):
                st.markdown("### 🌟 Guidance")
                st.markdown(result['response'])
                
                # Show relevant verses
                if context.get('used_verses'):
                    with st.expander("📖 Relevant Verses Referenced", expanded=False):
                        for verse in context['used_verses']:
                            st.markdown(f"""
                            **Chapter {verse['chapter']}, Verse {verse['verse']}**  
                            *Theme: {verse.get('theme', 'General')}*
                            
                            {verse['text']}
                            
                            ---
                            """)
                
                # Show themes
                if context.get('query_themes'):
                    st.markdown("### 🎭 Key Themes")
                    theme_cols = st.columns(len(context['query_themes']))
                    for i, theme in enumerate(context['query_themes']):
                        with theme_cols[i]:
                            st.markdown(f"**{theme.title()}**")
            else:
                st.error(f"Error generating response: {result['response']}")
        
        elif submit_button:
            st.warning("Please enter a question to receive guidance.")
    
    with tab2:
        st.markdown("### 🎯 Try These Sample Questions")
        
        sample_queries = [
            "I'm feeling depressed and lost",
            "How do I handle work stress?",
            "What should I do when I fail?",
            "I'm confused about my life purpose",
            "How to deal with difficult people?"
        ]
        
        for i, sample_query in enumerate(sample_queries):
            if st.button(sample_query, key=f"sample_{i}"):
                st.session_state.current_query = sample_query
                st.switch_page("💬 Ask Question")
                st.rerun()

else:
    st.error("Could not load Gita verses. Please check the data file.")
    st.info("Ensure the 'data/reformatted_bhagavad_gita.json' file is present in the repository.")
