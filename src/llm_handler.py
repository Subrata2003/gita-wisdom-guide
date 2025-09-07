import os
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GitaLLMHandler:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize the LLM handler"""
        self.model_name = model_name
        
        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            print("Warning: GOOGLE_API_KEY not found. Please set it in .env file")
            self.model = None
        
        # System prompt for Krishna-style responses
        self.system_prompt = """You are a wise guide inspired by the teachings of Krishna in the Bhagavad Gita. Your responses should:

1. Be compassionate, wise, and gentle
2. Draw from the philosophical teachings of the Gita
3. Speak with the wisdom and authority of a spiritual teacher
4. Use inclusive language that helps seekers of all backgrounds
5. Provide practical guidance rooted in spiritual wisdom
6. Always reference the relevant verses when possible
7. Acknowledge human struggles with empathy
8. Guide towards dharma (righteous action) and inner peace

Important: For serious mental health concerns, acknowledge the wisdom while also suggesting professional support.

Your tone should be:
- Wise and compassionate
- Patient and understanding
- Authoritative yet humble
- Encouraging and uplifting
"""
    
    def create_response_prompt(self, user_query: str, context: Dict) -> str:
        """Create the full prompt for generating response"""
        
        # Extract relevant information from context
        verses_text = context.get('formatted_context', '')
        themes = context.get('query_themes', [])
        
        prompt = f"""{self.system_prompt}

User's Question: "{user_query}"

Relevant Bhagavad Gita Verses:
{verses_text}

Key Themes Identified: {', '.join(themes)}

Based on these sacred teachings, provide a response that:
1. Addresses the user's concern with compassion
2. References the relevant verses naturally
3. Provides actionable spiritual guidance
4. Maintains the wisdom and tone of a spiritual teacher
5. If this is about serious mental health concerns, acknowledge the wisdom while also encouraging professional help

Begin your response by acknowledging the seeker's question, then provide guidance based on the eternal wisdom of the Gita."""
        
        return prompt
    
    def generate_response(self, user_query: str, context: Dict) -> Dict:
        """Generate a response using the LLM"""
        if not self.model:
            return {
                'response': "I apologize, but the AI service is not properly configured. Please check your API keys.",
                'error': True
            }
        
        try:
            # Create the full prompt
            full_prompt = self.create_response_prompt(user_query, context)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Check for safety concerns or mental health keywords
            response_text = response.text
            if self._needs_mental_health_disclaimer(user_query):
                response_text += "\n\n*Note: While spiritual wisdom provides great comfort, if you're experiencing persistent distress, please also consider speaking with a mental health professional or counselor.*"
            
            return {
                'response': response_text,
                'used_verses': context.get('used_verses', []),
                'themes': context.get('query_themes', []),
                'error': False
            }
            
        except Exception as e:
            return {
                'response': f"I encountered an difficulty in providing guidance: {str(e)}",
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
    
    def generate_simple_response(self, user_query: str) -> str:
        """Generate a simple response without context (fallback)"""
        if not self.model:
            return "I apologize, but I cannot provide guidance at this moment."
        
        simple_prompt = f"""{self.system_prompt}

User's Question: "{user_query}"

Provide a compassionate response based on the general wisdom of the Bhagavad Gita, even without specific verse references."""
        
        try:
            response = self.model.generate_content(simple_prompt)
            return response.text
        except Exception as e:
            return f"I encountered a difficulty in providing guidance: {str(e)}"

# Alternative handler for OpenAI API (if preferred)
class OpenAIGitaHandler:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """Initialize OpenAI handler"""
        import openai
        
        self.model_name = model_name
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key:
            openai.api_key = api_key
            self.client = openai
        else:
            print("Warning: OPENAI_API_KEY not found")
            self.client = None
    
    def generate_response(self, user_query: str, context: Dict) -> Dict:
        """Generate response using OpenAI"""
        if not self.client:
            return {'response': "OpenAI API not configured", 'error': True}
        
        try:
            system_message = """You are a wise spiritual guide inspired by Krishna's teachings in the Bhagavad Gita. 
            Provide compassionate, wise guidance drawing from the Gita's philosophy."""
            
            verses_text = context.get('formatted_context', '')
            
            user_message = f"""Question: {user_query}
            
Relevant Gita verses:
{verses_text}

Please provide guidance based on these teachings."""
            
            response = self.client.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                'response': response.choices[0].message.content,
                'used_verses': context.get('used_verses', []),
                'error': False
            }
            
        except Exception as e:
            return {'response': f"Error: {str(e)}", 'error': True}

# Usage example
if __name__ == "__main__":
    # Test the LLM handler
    llm_handler = GitaLLMHandler()
    
    # Sample context (would come from retriever)
    sample_context = {
        'formatted_context': "Chapter 2, Verse 47: You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions.",
        'used_verses': [{'chapter': 2, 'verse': 47}],
        'query_themes': ['action', 'detachment']
    }
    
    test_query = "I am stressed about work results"
    result = llm_handler.generate_response(test_query, sample_context)
    
    if not result['error']:
        print("Generated Response:")
        print(result['response'])
    else:
        print("Error:", result['response'])