#!/usr/bin/env python3
"""
Setup script for Gita Wisdom Guide
This script processes the data and initializes the vector database
"""

import os
import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.append('src')

from src.data_processor import GitaDataProcessor
from src.vector_store import GitaVectorStore

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'vector_db', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_data_files():
    """Check if data files exist"""
    required_files = [
        'data/reformatted_bhagavad_gita.json',
        # Add other required files here
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure your Bhagavad Gita JSON file is in the data/ directory")
        return False
    
    print("✓ All required data files found")
    return True

def process_gita_data():
    """Process the Bhagavad Gita data"""
    print("📚 Processing Bhagavad Gita data...")
    
    try:
        processor = GitaDataProcessor()
        
        # Process the data
        processed_data = processor.process_complete_dataset(
            'data/reformatted_bhagavad_gita.json',
            'data/processed_gita_data.json'
        )
        
        # Get and display statistics
        stats = processor.get_statistics()
        print("\n📊 Dataset Statistics:")
        for key, value in stats.items():
            if isinstance(value, list):
                print(f"   {key}: {', '.join(value)}")
            else:
                print(f"   {key}: {value}")
        
        print(f"✓ Processed {len(processed_data)} documents")
        return True
        
    except Exception as e:
        print(f"❌ Error processing data: {str(e)}")
        return False

def initialize_vector_database():
    """Initialize the vector database"""
    print("\n🔍 Initializing vector database...")
    
    try:
        # Check if processed data exists
        if not Path('data/processed_gita_data.json').exists():
            print("❌ Processed data file not found. Please run data processing first.")
            return False
        
        # Initialize vector store
        vector_store = GitaVectorStore()
        
        # Load and index data
        vector_store.load_and_index_data('data/processed_gita_data.json')
        
        # Get collection info
        info = vector_store.get_collection_info()
        print(f"✓ Vector database initialized with {info['document_count']} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing vector database: {str(e)}")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    google_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not google_key and not openai_key:
        print("⚠️  Warning: No API keys found")
        print("   Please set GOOGLE_API_KEY or OPENAI_API_KEY in your .env file")
        print("   You can get a free Gemini API key from: https://makersuite.google.com/app/apikey")
        return False
    
    if google_key:
        print("✓ Google/Gemini API key found")
    if openai_key:
        print("✓ OpenAI API key found")
    
    return True

def test_system():
    """Test the complete system"""
    print("\n🧪 Testing system...")
    
    try:
        from src.vector_store import GitaVectorStore
        from src.retrieval import GitaRetriever
        from src.llm_handler import GitaLLMHandler
        
        # Test vector store
        vector_store = GitaVectorStore()
        info = vector_store.get_collection_info()
        print(f"✓ Vector store: {info['document_count']} documents")
        
        # Test retrieval
        retriever = GitaRetriever(vector_store)
        test_query = "how to find peace"
        context = retriever.create_context_for_llm(test_query)
        print(f"✓ Retrieval: Found {context['total_verses']} relevant verses")
        
        # Test LLM (if API key available)
        if os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY'):
            llm_handler = GitaLLMHandler()
            print("✓ LLM handler initialized")
        else:
            print("⚠️  LLM handler not tested (no API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🕉️  Gita Wisdom Guide Setup")
    print("=" * 40)
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Check data files
    if not check_data_files():
        sys.exit(1)
    
    # Step 3: Process data
    if not process_gita_data():
        sys.exit(1)
    
    # Step 4: Initialize vector database
    if not initialize_vector_database():
        sys.exit(1)
    
    # Step 5: Check API keys
    api_configured = check_api_keys()
    
    # Step 6: Test system
    if not test_system():
        sys.exit(1)
    
    # Success message
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. If you haven't already, set your API key in .env file")
    print("2. Run the application: streamlit run src/app.py")
    
    if not api_configured:
        print("\n⚠️  Note: You'll need to configure an API key to use the LLM features")

if __name__ == "__main__":
    main()