#!/usr/bin/env python3
"""
Main runner script for Gita Wisdom Guide
Provides easy commands to manage the application
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_setup():
    """Run the setup process"""
    print("Running setup...")
    subprocess.run([sys.executable, "setup.py"])

def run_app():
    """Run the Streamlit application"""
    print("Starting Gita Wisdom Guide...")
    subprocess.run(["streamlit", "run", "src/app.py"])

def check_dependencies():
    """Check if all dependencies are installed"""
    # Map package names to their actual import names
    package_imports = {
        'streamlit': 'streamlit',
        'chromadb': 'chromadb', 
        'sentence-transformers': 'sentence_transformers',
        'google-generativeai': 'google.generativeai',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'python-dotenv': 'dotenv',
        'langchain': 'langchain'
    }
    
    missing = []
    for package, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("All dependencies are installed.")
    return True

def reset_database():
    """Reset the vector database"""
    import shutil
    vector_db_path = Path("vector_db")
    if vector_db_path.exists():
        shutil.rmtree(vector_db_path)
        print("Vector database reset.")
    else:
        print("No vector database found to reset.")

def main():
    parser = argparse.ArgumentParser(description="Gita Wisdom Guide Manager")
    parser.add_argument('command', choices=[
        'setup', 'run', 'check', 'reset', 'install'
    ], help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        run_setup()
    elif args.command == 'run':
        if not check_dependencies():
            sys.exit(1)
        run_app()
    elif args.command == 'check':
        check_dependencies()
    elif args.command == 'reset':
        reset_database()
    elif args.command == 'install':
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Gita Wisdom Guide Manager")
        print("Available commands:")
        print("  python run.py setup    - Initialize the system")
        print("  python run.py run      - Start the application")
        print("  python run.py check    - Check dependencies")
        print("  python run.py reset    - Reset vector database")
        print("  python run.py install  - Install dependencies")
    else:
        main()