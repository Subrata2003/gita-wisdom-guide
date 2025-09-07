import streamlit as st

# MUST be the very first Streamlit command - before any other imports or code
st.set_page_config(
    page_title="Gita Wisdom Guide",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from data_processor import GitaDataProcessor
from vector_store import GitaVectorStore
from retrieval import GitaRetriever
from llm_handler import GitaLLMHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitaWisdomApp:
    def __init__(self):
        """Initialize the Gita Wisdom Guide application"""
        # No page config here - it's already done above
        pass
    
    @st.cache_resource
    def initialize_components(_self):
        """Initialize and cache components"""
        try:
            # Initialize vector store
            vector_store = GitaVectorStore()
            
            # Initialize retriever
            retriever = GitaRetriever(vector_store)
            
            # Initialize LLM handler
            llm_handler = GitaLLMHandler()
            
            return vector_store, retriever, llm_handler, None
            
        except Exception as e:
            return None, None, None, str(e)
    
    def render_header(self):
        """Render the application header"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #ff6b35; font-size: 3rem; margin-bottom: 0;">🕉️ Gita Wisdom Guide</h1>
            <p style="font-size: 1.2rem; color: #666; margin-top: 0;">
                Discover timeless wisdom from the Bhagavad Gita for modern life challenges
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self, vector_store):
        """Render the sidebar with information and controls"""
        with st.sidebar:
            st.header("📚 About")
            st.markdown("""
            This guide draws wisdom from the **Bhagavad Gita** to help you navigate life's challenges with spiritual insight.
            
            **How it works:**
            1. Ask any question about life, work, relationships, or spirituality
            2. The system finds relevant verses from the Gita
            3. Receive guidance inspired by Krishna's teachings
            """)
            
            if vector_store:
                st.header("📊 Database Info")
                info = vector_store.get_collection_info()
                st.metric("Total Verses", info.get('document_count', 0))
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
            
            # Credit section
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <p style="color: #666; font-size: 0.9rem;">
                    Made with ❤️ by <strong>Subrata Bhuin </strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def process_query(self, query: str, retriever, llm_handler):
        """Process user query and generate response"""
        with st.spinner("🔍 Searching for relevant wisdom..."):
            # Retrieve relevant context
            context = retriever.create_context_for_llm(query)
        
        with st.spinner("💭 Generating guidance..."):
            # Generate response
            result = llm_handler.generate_response(query, context)
        
        return result, context
    
    def display_response(self, result: dict, context: dict):
        """Display the generated response and relevant verses"""
        if result.get('error'):
            st.error(f"Error generating response: {result['response']}")
            return
        
        # Main response
        st.markdown("### 🌟 Guidance")
        st.markdown(result['response'])
        
        # Show relevant verses in expandable section
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
            cols = st.columns(len(context['query_themes']))
            for i, theme in enumerate(context['query_themes']):
                cols[i].markdown(f"**{theme.title()}**")
    
    def render_main_interface(self, retriever, llm_handler):
        """Render the main chat interface"""
        st.markdown("### 💬 Ask Your Question")
        
        # Query input
        query = st.text_area(
            "What guidance do you seek?",
            placeholder="Type your question here... (e.g., 'I'm feeling overwhelmed at work')",
            height=100
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submit_button = st.button("🔮 Get Guidance", type="primary")
        with col2:
            if st.button("🧹 Clear"):
                st.rerun()
        
        # Process query
        if submit_button and query.strip():
            if not retriever or not llm_handler:
                st.error("System not properly initialized. Please check your configuration.")
                return
            
            # Process and display
            result, context = self.process_query(query, retriever, llm_handler)
            self.display_response(result, context)
        
        elif submit_button:
            st.warning("Please enter a question to receive guidance.")
    
    def render_sample_queries(self, retriever, llm_handler):
        """Render sample queries section"""
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
                result, context = self.process_query(sample_query, retriever, llm_handler)
                st.markdown(f"**Question:** {sample_query}")
                self.display_response(result, context)
    
    def run(self):
        """Run the main application"""
        # Initialize components
        vector_store, retriever, llm_handler, error = self.initialize_components()
        
        # Render header
        self.render_header()
        
        # Check for initialization errors
        if error:
            st.error(f"Failed to initialize application: {error}")
            st.markdown("""
            **Common issues:**
            1. Make sure you've processed the data first: `python setup.py`
            2. Check that your API keys are set in the .env file
            3. Ensure all dependencies are installed: `python run.py install`
            """)
            return
        
        # Render sidebar
        self.render_sidebar(vector_store)
        
        # Main content
        tab1, tab2 = st.tabs(["💬 Ask Question", "🎯 Sample Queries"])
        
        with tab1:
            self.render_main_interface(retriever, llm_handler)
        
        with tab2:
            self.render_sample_queries(retriever, llm_handler)

def apply_custom_styling():
    """Apply custom CSS styling"""
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

def main():
    """Main function to run the app"""
    # Apply styling
    apply_custom_styling()
    
    # Create and run app
    app = GitaWisdomApp()
    app.run()

if __name__ == "__main__":
    main()