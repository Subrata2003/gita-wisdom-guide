#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment
This file should be in the root directory for Streamlit Cloud to detect it
"""

import streamlit as st

# Configure page first (required by Streamlit)
st.set_page_config(
    page_title="Gita Wisdom Guide",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the main app
try:
    from app_fixed import GitaWisdomApp, apply_custom_styling
    
    def main():
        """Main function to run the app"""
        # Check if this is the first run (no vector db)
        vector_db_path = Path("vector_db")
        processed_data_path = Path("data/processed_gita_data.json")
        
        if not vector_db_path.exists() or not processed_data_path.exists():
            st.warning("⚠️ Setting up the system for first use...")
            
            # Run setup automatically
            try:
                from data_processor import GitaDataProcessor
                from vector_store import GitaVectorStore
                
                with st.spinner("📚 Processing Gita data..."):
                    # Process data if needed
                    if not processed_data_path.exists():
                        processor = GitaDataProcessor()
                        processor.process_complete_dataset(
                            'data/reformatted_bhagavad_gita.json',
                            'data/processed_gita_data.json'
                        )
                        st.success("✅ Data processed successfully!")
                
                with st.spinner("🔍 Initializing vector database..."):
                    # Initialize vector store
                    vector_store = GitaVectorStore()
                    vector_store.load_and_index_data('data/processed_gita_data.json')
                    st.success("✅ Vector database initialized!")
                
                st.info("🔄 Please refresh the page to continue...")
                st.stop()
                
            except Exception as e:
                st.error(f"❌ Setup failed: {str(e)}")
                st.info("Please check if your data files are properly uploaded.")
                st.stop()
        
        # Apply styling
        apply_custom_styling()
        
        # Create and run app
        app = GitaWisdomApp()
        app.run()

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"❌ Import error: {str(e)}")
    st.markdown("""
    **Setup Required:**
    1. Ensure all files are properly uploaded
    2. Check that your API key is configured in Streamlit secrets
    3. Verify the data files are in the correct location
    """)