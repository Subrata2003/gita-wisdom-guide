# Gita Wisdom Guide

> *"You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions."* - Bhagavad Gita 2.47

A modern AI-powered application that provides spiritual guidance from the Bhagavad Gita to help navigate contemporary life challenges through ancient wisdom.

## Overview

Gita Wisdom Guide combines advanced natural language processing with the timeless teachings of the Bhagavad Gita to offer personalized spiritual guidance. The system uses Retrieval-Augmented Generation (RAG) to find relevant verses and generate contextual responses inspired by Krishna's teachings.

## Key Features

- **Intelligent Semantic Search**: Vector-based similarity matching to find relevant verses  
- **AI-Generated Guidance**: Contextual responses powered by Google Gemini  
- **Theme-Based Organization**: Automatic categorization by spiritual themes (peace, duty, action, etc.)  
- **Responsive Web Interface**: Clean, intuitive UI built with Streamlit  
- **Real-time Processing**: Instant verse retrieval and response generation  

## Architecture
User Query → Vector Search → Relevant Verses → LLM + Context → Wisdom Response


### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Processor** | Python, Pandas | Cleans and structures Gita verses |
| **Vector Store** | ChromaDB | Semantic search and verse retrieval |
| **Retrieval Engine** | Sentence Transformers | Theme-based and similarity search |
| **LLM Handler** | Google Gemini API | Generates Krishna-inspired responses |
| **Web Interface** | Streamlit | User interaction and response display |


