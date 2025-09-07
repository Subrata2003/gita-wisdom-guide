import streamlit as st
import sys
import sqlite3
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

st.set_page_config(
    page_title="Gita Wisdom Guide",
    page_icon="🕉️",
    layout="wide"
)

import json
import google.generativeai as genai

st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #ff6b35; font-size: 3rem;">🕉️ Gita Wisdom Guide</h1>
    <p style="font-size: 1.2rem; color: #666;">
        Discover timeless wisdom from the Bhagavad Gita
    </p>
</div>
""", unsafe_allow_html=True)

# Configure API
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Load data
    @st.cache_data
    def load_verses():
        try:
            with open('data/reformatted_bhagavad_gita.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    verses = load_verses()
    
    # Sidebar
    with st.sidebar:
        st.header("📚 About")
        st.write("AI-powered spiritual guidance from the Bhagavad Gita")
        if verses:
            st.metric("Verses Loaded", len(verses))
        st.markdown("---")
        st.markdown("Made with ❤️ by **Subrata**")
    
    # Main interface
    query = st.text_area(
        "What guidance do you seek?",
        placeholder="e.g., 'I'm feeling stressed and overwhelmed'",
        height=100
    )
    
    if st.button("🔮 Get Guidance", type="primary"):
        if query:
            with st.spinner("Generating wisdom..."):
                prompt = f"""
                You are a wise spiritual guide inspired by Krishna's teachings in the Bhagavad Gita.
                
                Question: {query}
                
                Provide compassionate guidance based on the wisdom of the Bhagavad Gita. 
                Include practical advice while maintaining the spiritual depth of the teachings.
                Reference relevant concepts from the Gita when appropriate.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### 🌟 Guidance")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
        else:
            st.warning("Please enter your question")
    
    # Sample questions
    st.markdown("### 🎯 Try These Sample Questions")
    samples = [
        "I'm feeling stressed at work",
        "How do I deal with failure?", 
        "What is my purpose in life?",
        "How to handle difficult relationships?"
    ]
    
    cols = st.columns(2)
    for i, sample in enumerate(samples):
        with cols[i % 2]:
            if st.button(sample, key=sample):
                # Auto-fill the text area
                st.session_state.query = sample
                st.rerun()
            
else:
    st.error("Please configure GOOGLE_API_KEY in Streamlit secrets")
