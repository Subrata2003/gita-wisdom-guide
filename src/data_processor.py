import pandas as pd
import json
import re
from typing import List, Dict

class GitaDataProcessor:
    def __init__(self):
        self.processed_data = []
    
    def load_json_data(self, file_path: str) -> List[Dict]:
        """Load data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Load data from CSV file"""
        return pd.read_csv(file_path)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Sanskrit diacritics
        text = re.sub(r'[^\w\s\u0900-\u097F.,;:!?()-]', '', text)
        return text.strip()
    
    def process_verses(self, data: List[Dict]) -> List[Dict]:
        """Process individual verses and create metadata"""
        processed = []
        
        for verse in data:
            processed_verse = {
                'chapter': verse['chapter'],
                'verse': verse['verse'],
                'text': self.clean_text(verse['text']),
                'verse_id': f"Chapter {verse['chapter']}, Verse {verse['verse']}",
                'content_type': 'verse',
                'word_count': len(verse['text'].split()),
                'theme': self.extract_theme(verse['text'])
            }
            processed.append(processed_verse)
        
        return processed
    
    def extract_theme(self, text: str) -> str:
        """Extract basic theme from verse content"""
        text_lower = text.lower()
        
        # Define theme keywords
        themes = {
            'duty': ['duty', 'dharma', 'righteous', 'obligation'],
            'detachment': ['attachment', 'detachment', 'renunciation', 'surrender'],
            'knowledge': ['knowledge', 'wisdom', 'understand', 'realize'],
            'devotion': ['devotion', 'worship', 'love', 'surrender'],
            'action': ['action', 'work', 'perform', 'activity'],
            'soul': ['soul', 'self', 'atman', 'eternal'],
            'peace': ['peace', 'tranquil', 'calm', 'serenity'],
            'meditation': ['meditation', 'yoga', 'mind', 'concentration']
        }
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
        
        return 'general'
    
    def create_chunks(self, processed_data: List[Dict], chunk_size: int = 3) -> List[Dict]:
        """Create chunks of verses for better context"""
        chunks = []
        
        for i in range(0, len(processed_data), chunk_size):
            chunk_verses = processed_data[i:i + chunk_size]
            
            # Combine text from multiple verses
            combined_text = " ".join([v['text'] for v in chunk_verses])
            
            chunk = {
                'chunk_id': f"chunk_{i//chunk_size + 1}",
                'chapter_range': f"{chunk_verses[0]['chapter']}-{chunk_verses[-1]['chapter']}",
                'verse_range': f"{chunk_verses[0]['verse']}-{chunk_verses[-1]['verse']}",
                'text': combined_text,
                'verses': chunk_verses,
                'content_type': 'chunk',
                'theme': chunk_verses[0]['theme']  # Take theme from first verse
            }
            chunks.append(chunk)
        
        return chunks
    
    def process_complete_dataset(self, json_path: str, output_path: str = None) -> List[Dict]:
        """Complete processing pipeline"""
        # Load data
        raw_data = self.load_json_data(json_path)
        
        # Process verses
        processed_verses = self.process_verses(raw_data)
        
        # Create chunks
        chunks = self.create_chunks(processed_verses)
        
        # Combine individual verses and chunks
        self.processed_data = processed_verses + chunks
        
        # Save if output path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
        
        return self.processed_data
    
    def get_statistics(self) -> Dict:
        """Get basic statistics about the dataset"""
        if not self.processed_data:
            return {}
        
        verses = [d for d in self.processed_data if d['content_type'] == 'verse']
        chunks = [d for d in self.processed_data if d['content_type'] == 'chunk']
        
        return {
            'total_verses': len(verses),
            'total_chunks': len(chunks),
            'total_chapters': max([v['chapter'] for v in verses]),
            'avg_words_per_verse': sum([v['word_count'] for v in verses]) / len(verses),
            'themes': list(set([v['theme'] for v in verses]))
        }

# Usage example
if __name__ == "__main__":
    processor = GitaDataProcessor()
    
    # Process the data
    processed_data = processor.process_complete_dataset(
        'data/reformatted_bhagavad_gita.json',
        'data/processed_gita_data.json'
    )
    
    # Print statistics
    stats = processor.get_statistics()
    print("Dataset Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")