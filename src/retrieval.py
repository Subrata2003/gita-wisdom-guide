from typing import List, Dict, Optional
from vector_store import GitaVectorStore
import re

class GitaRetriever:
    def __init__(self, vector_store: GitaVectorStore):
        """Initialize the retriever with a vector store"""
        self.vector_store = vector_store
        
        # Define topic-theme mapping for better retrieval
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
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess the user query"""
        query = query.lower().strip()
        
        # Expand common abbreviations and informal language
        expansions = {
            "i'm": "I am",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "what should i do": "how should I act",
            "help me": "guide me",
            "i feel": "I am experiencing"
        }
        
        for abbrev, expanded in expansions.items():
            query = query.replace(abbrev, expanded)
        
        return query
    
    def extract_query_themes(self, query: str) -> List[str]:
        """Extract relevant themes from the query"""
        query_lower = query.lower()
        relevant_themes = []
        
        for topic, themes in self.topic_themes.items():
            if topic in query_lower:
                relevant_themes.extend(themes)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(relevant_themes)) if relevant_themes else ['general']
    
    def retrieve_relevant_verses(self, query: str, max_results: int = 8) -> List[Dict]:
        """Retrieve relevant verses for a given query"""
        processed_query = self.preprocess_query(query)
        themes = self.extract_query_themes(processed_query)
        
        all_results = []
        
        # Search by themes first
        for theme in themes[:2]:  # Limit to top 2 themes
            theme_results = self.vector_store.search_by_theme(
                processed_query, theme, n_results=3
            )
            all_results.extend(self._format_results(theme_results))
        
        # General semantic search
        general_results = self.vector_store.search_similar(
            processed_query, n_results=5
        )
        all_results.extend(self._format_results(general_results))
        
        # Remove duplicates and sort by relevance
        unique_results = self._remove_duplicates(all_results)
        
        # Return top results
        return unique_results[:max_results]
    
    def _format_results(self, raw_results: Dict) -> List[Dict]:
        """Format raw search results into structured format"""
        formatted = []
        
        if not raw_results['documents'] or not raw_results['documents'][0]:
            return formatted
        
        for doc, metadata, distance in zip(
            raw_results['documents'][0],
            raw_results['metadatas'][0], 
            raw_results['distances'][0]
        ):
            formatted_result = {
                'text': doc,
                'chapter': int(metadata.get('chapter', 0)) if metadata.get('chapter', '').isdigit() else 0,
                'verse': int(metadata.get('verse', 0)) if metadata.get('verse', '').isdigit() else 0,
                'verse_id': metadata.get('verse_id', ''),
                'theme': metadata.get('theme', 'general'),
                'content_type': metadata.get('content_type', 'verse'),
                'relevance_score': 1 - distance,  # Convert distance to similarity
                'distance': distance
            }
            formatted.append(formatted_result)
        
        return formatted
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on verse_id"""
        seen = set()
        unique_results = []
        
        for result in results:
            verse_id = result.get('verse_id', '')
            if verse_id and verse_id not in seen:
                seen.add(verse_id)
                unique_results.append(result)
            elif not verse_id:  # For chunks or other content
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return unique_results
    
    def get_contextual_verses(self, chapter: int, verse: int, context_size: int = 2) -> List[Dict]:
        """Get verses around a specific verse for context"""
        context_results = []
        
        for v in range(max(1, verse - context_size), verse + context_size + 1):
            try:
                results = self.vector_store.search_by_chapter(
                    f"Chapter {chapter} Verse {v}", chapter, n_results=1
                )
                if results['documents'] and results['documents'][0]:
                    context_results.extend(self._format_results(results))
            except:
                continue
        
        return context_results
    
    def create_context_for_llm(self, query: str, max_context_length: int = 2000) -> Dict:
        """Create formatted context for LLM consumption"""
        relevant_verses = self.retrieve_relevant_verses(query)
        
        context_parts = []
        total_length = 0
        used_verses = []
        
        for verse in relevant_verses:
            verse_text = f"Chapter {verse['chapter']}, Verse {verse['verse']}: {verse['text']}"
            
            if total_length + len(verse_text) <= max_context_length:
                context_parts.append(verse_text)
                used_verses.append(verse)
                total_length += len(verse_text)
            else:
                break
        
        context = {
            'formatted_context': '\n\n'.join(context_parts),
            'used_verses': used_verses,
            'query_themes': self.extract_query_themes(query),
            'total_verses': len(used_verses)
        }
        
        return context

# Usage example
if __name__ == "__main__":
    # Initialize components
    vector_store = GitaVectorStore()
    retriever = GitaRetriever(vector_store)
    
    # Test retrieval
    test_query = "I am feeling depressed and lost in life"
    context = retriever.create_context_for_llm(test_query)
    
    print(f"Query: {test_query}")
    print(f"Relevant themes: {context['query_themes']}")
    print(f"Total verses found: {context['total_verses']}")
    print("\nRelevant verses:")
    print(context['formatted_context'])