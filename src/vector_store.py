import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict, Optional
import uuid

class GitaVectorStore:
    def __init__(self, collection_name: str = "gita_wisdom", persist_directory: str = "./vector_db"):
        """Initialize the vector store"""
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Bhagavad Gita verses and wisdom"}
        )
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for given texts"""
        return self.embedding_model.encode(texts).tolist()
    
    def add_documents(self, documents: List[Dict]) -> None:
        """Add documents to the vector store"""
        texts = []
        metadatas = []
        ids = []
        
        for doc in documents:
            # Create unique ID
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            
            # Extract text
            texts.append(doc['text'])
            
            # Prepare metadata (ChromaDB requires string values)
            metadata = {
                'chapter': str(doc.get('chapter', '')),
                'verse': str(doc.get('verse', '')),
                'verse_id': doc.get('verse_id', ''),
                'content_type': doc.get('content_type', 'verse'),
                'theme': doc.get('theme', 'general')
            }
            
            # Add chunk-specific metadata if available
            if 'chunk_id' in doc:
                metadata['chunk_id'] = doc['chunk_id']
                metadata['chapter_range'] = doc.get('chapter_range', '')
                metadata['verse_range'] = doc.get('verse_range', '')
            
            metadatas.append(metadata)
        
        # Create embeddings
        embeddings = self.embed_texts(texts)
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to vector store")
    
    def search_similar(self, query: str, n_results: int = 5, 
                      filter_metadata: Optional[Dict] = None) -> Dict:
        """Search for similar documents"""
        # Create query embedding
        query_embedding = self.embed_texts([query])[0]
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results
    
    def search_by_theme(self, query: str, theme: str, n_results: int = 3) -> Dict:
        """Search documents filtered by theme"""
        filter_metadata = {"theme": theme}
        return self.search_similar(query, n_results, filter_metadata)
    
    def search_by_chapter(self, query: str, chapter: int, n_results: int = 3) -> Dict:
        """Search documents filtered by chapter"""
        filter_metadata = {"chapter": str(chapter)}
        return self.search_similar(query, n_results, filter_metadata)
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "embedding_model": "all-MiniLM-L6-v2"
        }
    
    def load_and_index_data(self, data_path: str) -> None:
        """Load processed data and create vector index"""
        with open(data_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # Clear existing collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Bhagavad Gita verses and wisdom"}
        )
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.add_documents(batch)
        
        print(f"Successfully indexed {len(documents)} documents")

# Usage example
if __name__ == "__main__":
    # Initialize vector store
    vector_store = GitaVectorStore()
    
    # Load and index the processed data
    vector_store.load_and_index_data('data/processed_gita_data.json')
    
    # Test search
    results = vector_store.search_similar("How to deal with depression and sadness?", n_results=3)
    
    print("Search Results:")
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        print(f"\nResult {i+1} (Distance: {distance:.3f}):")
        print(f"Chapter {metadata['chapter']}, Verse {metadata['verse']}")
        print(f"Theme: {metadata['theme']}")
        print(f"Text: {doc[:200]}...")