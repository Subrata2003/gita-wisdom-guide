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

def classify_question_type(query: str) -> str:
    """Classify the type of question being asked"""
    query_lower = query.lower()
    
    # Factual question patterns
    factual_patterns = [
        'who wrote', 'who is the author', 'when was written', 'when was composed',
        'how many chapters', 'how many verses', 'what is the meaning of',
        'who is krishna', 'who is arjuna', 'what is dharma', 'what is karma',
        'when did', 'where was', 'what does', 'define', 'explain',
        'how many', 'which chapter', 'what chapter', 'tell me about',
        'who said', 'what is the story', 'summary of', 'overview of'
    ]
    
    # Check for factual patterns
    if any(pattern in query_lower for pattern in factual_patterns):
        return 'factual'
    
    # Personal guidance patterns
    guidance_patterns = [
        'i am', 'i feel', 'how do i', 'help me', 'what should i do',
        'i\'m feeling', 'i\'m confused', 'i\'m struggling', 'advice',
        'guidance', 'suggest', 'recommend'
    ]
    
    if any(pattern in query_lower for pattern in guidance_patterns):
        return 'guidance'
    
    return 'guidance'  # Default to guidance mode

# Custom CSS for Krishna-themed UI
st.markdown("""
<style>
/* Import Google Fonts for better typography */
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Poppins:wght@300;400;500;600&display=swap');

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main app background */
.stApp {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
}

/* Main container background with Krishna image */
.main .block-container {
    background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.5)), 
                url('https://raw.githubusercontent.com/Subrata2003/gita-wisdom-guide/main/assets/krishna_background.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    min-height: 90vh;
}

/* Content containers with glassmorphism effect */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(15px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 10px;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: white !important;
    font-weight: 500;
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    padding: 12px 20px;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(255, 107, 53, 0.8);
    color: white !important;
}

/* Text areas and inputs */
.stTextArea textarea {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 15px !important;
    color: #2c3e50 !important;
    font-family: 'Lora', serif;
    font-size: 16px !important;
    padding: 15px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stTextArea textarea:focus {
    border-color: #ff6b35 !important;
    box-shadow: 0 0 20px rgba(255, 107, 53, 0.4) !important;
    background: rgba(255, 255, 255, 0.98) !important;
}

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
    padding: 0.6rem 2rem;
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
    transition: all 0.3s ease;
    font-size: 16px;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(255, 107, 53, 0.6);
    background: linear-gradient(135deg, #f7931e, #ff6b35) !important;
}

/* Secondary buttons (sample questions) */
.stButton > button {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #2c3e50 !important;
    border: 2px solid rgba(255, 107, 53, 0.4) !important;
    border-radius: 20px !important;
    font-family: 'Poppins', sans-serif;
    margin: 8px 0;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
    width: 100%;
}

.stButton > button:hover {
    background: rgba(255, 107, 53, 0.15) !important;
    border-color: #ff6b35 !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
}

/* Response containers */
div[data-testid="stMarkdownContainer"] {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

/* Headers and text styling */
h1 {
    color: white !important;
    font-family: 'Poppins', sans-serif !important;
    text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
    font-weight: 600;
    text-align: center;
}

h2, h3, h4, h5, h6 {
    color: #2c3e50 !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600;
}

.stMarkdown p {
    color: #2c3e50 !important;
    font-family: 'Lora', serif;
    line-height: 1.7;
    font-size: 16px;
}

.stMarkdown strong {
    color: #ff6b35 !important;
    font-weight: 600;
}

/* Sidebar styling */
.css-1d391kg, .css-1lcbmhc {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(15px);
    border-right: 2px solid rgba(255, 107, 53, 0.3);
}

.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
    color: #2c3e50 !important;
    text-shadow: none;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px;
    color: white !important;
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.streamlit-expanderContent {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    padding: 20px;
    margin-top: 10px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Metrics styling */
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    margin: 10px 0;
}

div[data-testid="metric-container"] label {
    color: #2c3e50 !important;
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
}

div[data-testid="metric-container"] div {
    color: #ff6b35 !important;
    font-size: 24px !important;
    font-weight: 600;
}

/* Alert messages */
.stAlert {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 12px;
    border: none !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* Spinner styling */
.stSpinner {
    color: #ff6b35 !important;
}

/* Column styling for themes */
.stColumns {
    gap: 15px;
}

/* Success/Error message styling */
.stSuccess {
    background: rgba(40, 167, 69, 0.9) !important;
    color: white !important;
    border-radius: 10px;
    backdrop-filter: blur(10px);
}

.stError {
    background: rgba(220, 53, 69, 0.9) !important;
    color: white !important;
    border-radius: 10px;
    backdrop-filter: blur(10px);
}

.stWarning {
    background: rgba(255, 193, 7, 0.9) !important;
    color: #2c3e50 !important;
    border-radius: 10px;
    backdrop-filter: blur(10px);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 107, 53, 0.7);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 107, 53, 0.9);
}
</style>
""", unsafe_allow_html=True)

# Enhanced header with Krishna theme
st.markdown("""
<div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
    <h1 style="color: white; font-size: 3.5rem; margin-bottom: 0; 
               text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
               font-family: 'Poppins', sans-serif; font-weight: 600;">
        🕉️ Gita Wisdom Guide
    </h1>
    <p style="font-size: 1.3rem; color: rgba(255, 255, 255, 0.95); margin-top: 10px;
              text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
              font-family: 'Lora', serif; font-style: italic;">
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
            self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
        else:
            self.model = None
    
    def generate_factual_response(self, query: str) -> Dict:
        """Generate a factual response for knowledge-based questions"""
        if not self.model:
            return {
                'response': "API service not properly configured. Please check your API keys.",
                'error': True
            }
        
        try:
            prompt = f"""
            You are a knowledgeable scholar of the Bhagavad Gita. Answer this factual question concisely and accurately:
            
            Question: {query}
            
            Guidelines:
            - Provide a direct, factual answer in 2-4 sentences
            - Include one relevant verse reference if applicable
            - Keep the response informative but brief
            - Use a scholarly but accessible tone
            - Focus on facts rather than spiritual guidance
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                'response': response.text,
                'used_verses': [],
                'themes': [],
                'error': False
            }
            
        except Exception as e:
            return {
                'response': f"I encountered a difficulty in providing information: {str(e)}",
                'error': True
            }
    
    def generate_response(self, query: str, context: Dict) -> Dict:
        """Generate response using the LLM for guidance questions"""
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
3. Provide practical guidance rooted in spiritual wisdom
4. Reference the relevant verses when possible
5. Acknowledge human struggles with empathy
6. Guide towards dharma (righteous action) and inner peace
7. Keep responses structured and reasonably concise
8. Use bullet points or numbered lists when appropriate

For serious mental health concerns, acknowledge the wisdom while also suggesting professional support."""

            prompt = f"""{system_prompt}

User's Question: "{query}"

Relevant Bhagavad Gita Verses:
{verses_text}

Key Themes Identified: {', '.join(themes)}

Based on these sacred teachings, provide a response that:
1. Addresses the user's concern with compassion (2-3 sentences)
2. References the relevant verses naturally (1-2 key verses)
3. Provides actionable spiritual guidance (3-4 practical points)
4. Keeps the total response under 250 words
5. Uses a structured format with clear sections"""

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
        **Factual Questions:**
        - "Who wrote the Bhagavad Gita?"
        - "How many chapters are there?"
        - "What is dharma?"
        
        **Guidance Questions:**
        - "I'm feeling stressed at work"
        - "How do I deal with failure?"
        - "What is my purpose in life?"
        """)
        
        st.header("⚠️ Disclaimer")
        st.markdown("""
        This tool provides spiritual guidance based on the Bhagavad Gita. 
        For serious mental health concerns, please consult a qualified professional.
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <p style="color: #ff6b35; font-size: 0.9rem; font-weight: 600;">
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
            placeholder="Type your question here... (e.g., 'I'm feeling overwhelmed at work' or 'Who wrote the Gita?')",
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
            # Determine question type
            question_type = classify_question_type(query)
            
            if question_type == 'factual':
                # Handle factual questions without verse lookup
                with st.spinner("📚 Generating information..."):
                    result = llm_handler.generate_factual_response(query)
                
                # Display factual response
                if not result.get('error'):
                    st.markdown("### 📖 Information")
                    st.markdown(result['response'])
                else:
                    st.error(f"Error generating response: {result['response']}")
            
            else:
                # Handle guidance questions with verse lookup (existing logic)
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
                
                # Display guidance response
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
        
        # Factual questions
        st.markdown("#### 📖 Factual Questions")
        factual_queries = [
            "Who wrote the Bhagavad Gita?",
            "How many chapters are in the Gita?",
            "What is dharma according to the Gita?"
        ]
        
        for i, sample_query in enumerate(factual_queries):
            if st.button(sample_query, key=f"factual_{i}"):
                # Process factual query directly
                with st.spinner("📚 Generating information..."):
                    result = llm_handler.generate_factual_response(sample_query)
                
                # Display the question and response
                st.markdown(f"**Question:** {sample_query}")
                
                if not result.get('error'):
                    st.markdown("### 📖 Information")
                    st.markdown(result['response'])
                else:
                    st.error(f"Error generating response: {result['response']}")
        
        st.markdown("#### 🌟 Guidance Questions")
        guidance_queries = [
            "I'm feeling depressed and lost",
            "How do I handle work stress?",
            "What should I do when I fail?",
            "I'm confused about my life purpose",
            "How to deal with difficult people?"
        ]
        
        for i, sample_query in enumerate(guidance_queries):
            if st.button(sample_query, key=f"guidance_{i}"):
                # Process the sample query directly with verse lookup
                with st.spinner("🔍 Searching for relevant wisdom..."):
                    # Find relevant verses
                    relevant_verses = retriever.find_relevant_verses(sample_query)
                    themes = retriever.extract_query_themes(sample_query)
                    
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
                    result = llm_handler.generate_response(sample_query, context)
                
                # Display the question and response
                st.markdown(f"**Question:** {sample_query}")
                
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
                        for j, theme in enumerate(context['query_themes']):
                            with theme_cols[j]:
                                st.markdown(f"**{theme.title()}**")
                else:
                    st.error(f"Error generating response: {result['response']}")

else:
    st.error("Could not load Gita verses. Please check the data file.")
    st.info("Ensure the 'data/reformatted_bhagavad_gita.json' file is present in the repository.")