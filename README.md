🕉️ Gita Wisdom Guide
A modern AI-powered guide that provides spiritual wisdom from the Bhagavad Gita to help navigate life's challenges.

Features
Semantic Search: Find relevant verses based on your questions using vector similarity
AI-Powered Guidance: Get thoughtful responses inspired by Krishna's teachings
Theme-Based Retrieval: Automatically categorizes and retrieves verses by themes like peace, duty, action, etc.
Beautiful UI: Clean, intuitive interface built with Streamlit
Multiple LLM Support: Works with Gemini Pro, OpenAI GPT, and other models
Quick Start
1. Installation
bash
# Clone or download the project
git clone <your-repo-url>
cd gita-wisdom-guide

# Install dependencies
pip install -r requirements.txt
2. Setup Data
Place your reformatted_bhagavad_gita.json file in the data/ directory.

3. Configure API Keys
Create a .env file in the root directory:

bash
# Get a free API key from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
4. Initialize the System
bash
python setup.py
5. Run the Application
bash
streamlit run src/app.py
System Architecture
User Query → Vector Search → Relevant Verses → LLM + Context → Wisdom Response
Components:
Data Processor: Cleans and structures Gita verses
Vector Store: ChromaDB for semantic search
Retrieval System: Finds relevant verses based on themes and similarity
LLM Handler: Generates Krishna-inspired responses
Streamlit App: User interface
Usage Examples
Sample Questions:
"I'm feeling stressed at work"
"How do I deal with failure?"
"What is my purpose in life?"
"How to handle difficult relationships?"
"I'm afraid of making decisions"
Response Format:
The system provides:

Compassionate guidance based on Gita teachings
References to relevant verses
Practical spiritual advice
Theme identification
Project Structure
gita-wisdom-guide/
├── src/
│   ├── data_processor.py    # Data cleaning and processing
│   ├── vector_store.py      # Vector database management
│   ├── retrieval.py         # Semantic search and retrieval
│   ├── llm_handler.py       # AI response generation
│   └── app.py              # Main Streamlit application
├── data/
│   ├── reformatted_bhagavad_gita.json
│   └── processed_gita_data.json
├── vector_db/              # ChromaDB storage
├── requirements.txt
├── setup.py               # Setup and initialization
├── .env                   # API keys (create this)
└── README.md
Technical Details
Vector Database
Engine: ChromaDB
Embeddings: all-MiniLM-L6-v2 (384 dimensions)
Storage: Persistent local storage
LLM Integration
Primary: Google Gemini Pro
Alternative: OpenAI GPT-3.5/4
Fallback: Local models via Hugging Face
Search Features
Semantic similarity search
Theme-based filtering
Chapter/verse specific queries
Context window management
API Keys
Gemini API (Recommended)
Visit Google AI Studio
Create a free API key
Add to .env file
OpenAI API (Alternative)
Visit OpenAI Platform
Create an API key (requires payment)
Add to .env file
Troubleshooting
Common Issues:
"No API key found"
Check your .env file
Ensure API key is valid
"Vector database not found"
Run python setup.py first
Check if data processing completed
"No relevant verses found"
Try rephrasing your question
Check if data was indexed properly
Getting Help:
Check the application logs
Verify all dependencies are installed
Ensure data files are in correct location
Ethical Considerations
This tool provides spiritual guidance based on ancient wisdom. For serious mental health concerns, please consult qualified professionals. The system includes appropriate disclaimers for mental health-related queries.

Contributing
Feel free to contribute improvements:

Better prompt engineering
Additional LLM integrations
UI/UX enhancements
More sophisticated retrieval algorithms
License
This project is for educational and spiritual guidance purposes. Please respect the sacred nature of the source material.

"You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions." - Bhagavad Gita 2.47

