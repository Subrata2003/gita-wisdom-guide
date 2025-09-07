import streamlit as st

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
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from data_processor import GitaDataProcessor
    from vector_store import GitaVectorStore
    from retrieval import GitaRetriever
    from llm_handler import GitaLLMHandler
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Main app logic inline
    def main():
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #ff6b35; font-size: 3rem; margin-bottom: 0;">🕉️ Gita Wisdom Guide</h1>
            <p style="font-size: 1.2rem; color: #666; margin-top: 0;">
                Discover timeless wisdom from the Bhagavad Gita for modern life challenges
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize components
        @st.cache_resource
        def initialize_components():
            try:
                vector_store = GitaVectorStore()
                retriever = GitaRetriever(vector_store)
                llm_handler = GitaLLMHandler()
                return vector_store, retriever, llm_handler, None
            except Exception as e:
                return None, None, None, str(e)
        
        vector_store, retriever, llm_handler, error = initialize_components()
        
        if error:
            st.error(f"Initialization failed: {error}")
            st.info("Setting up system for first use...")
            
            # Auto-setup
            try:
                processor = GitaDataProcessor()
                with st.spinner("Processing data..."):
                    processor.process_complete_dataset(
                        'data/reformatted_bhagavad_gita.json',
                        'data/processed_gita_data.json'
                    )
                
                with st.spinner("Initializing database..."):
                    vector_store = GitaVectorStore()
                    vector_store.load_and_index_data('data/processed_gita_data.json')
                
                st.success("Setup complete! Please refresh the page.")
                st.stop()
            except Exception as e:
                st.error(f"Setup failed: {str(e)}")
                st.stop()
        
        # Sidebar
        with st.sidebar:
            st.header("📚 About")
            st.markdown("This guide provides spiritual wisdom from the Bhagavad Gita using AI.")
            
            if vector_store:
                info = vector_store.get_collection_info()
                st.metric("Total Verses", info.get('document_count', 0))
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center;">
                <p style="color: #666; font-size: 0.9rem;">
                    Made with ❤️ by <strong>Subrata</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Main interface
        st.markdown("### 💬 Ask Your Question")
        query = st.text_area(
            "What guidance do you seek?",
            placeholder="e.g., 'I'm feeling overwhelmed at work'",
            height=100
        )
        
        if st.button("🔮 Get Guidance", type="primary"):
            if query.strip():
                with st.spinner("Searching for wisdom..."):
                    context = retriever.create_context_for_llm(query)
                    result = llm_handler.generate_response(query, context)
                
                if not result.get('error'):
                    st.markdown("### 🌟 Guidance")
                    st.markdown(result['response'])
                    
                    if context.get('used_verses'):
                        with st.expander("📖 Referenced Verses"):
                            for verse in context['used_verses']:
                                st.markdown(f"**Chapter {verse['chapter']}, Verse {verse['verse']}**")
                                st.markdown(verse['text'])
                                st.markdown("---")
                else:
                    st.error(f"Error: {result['response']}")
            else:
                st.warning("Please enter a question.")

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"Missing dependencies: {str(e)}")
    st.info("Ensure all source files are uploaded to the repository.")
