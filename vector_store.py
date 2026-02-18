"""
ChromaDB Vector Store for Insurance Policy Documents
Handles embedding generation, storage, and retrieval of policy documents
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PolicyVectorStore:
    """Vector store for insurance policy documents using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB vector store
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.collection_name = "insurance_policies"
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model (all-MiniLM-L6-v2 is fast and efficient)
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Embedding model loaded")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"✓ Loaded existing collection '{self.collection_name}'")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Insurance policy documents"}
            )
            logger.info(f"✓ Created new collection '{self.collection_name}'")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                overlap_words = []
                overlap_length = 0
                for w in reversed(current_chunk):
                    if overlap_length + len(w) + 1 <= overlap:
                        overlap_words.insert(0, w)
                        overlap_length += len(w) + 1
                    else:
                        break
                
                current_chunk = overlap_words
                current_length = overlap_length
            
            current_chunk.append(word)
            current_length += word_length
        
        # Add last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def ingest_pdf(self, pdf_path: str, metadata: Optional[Dict] = None) -> int:
        """
        Ingest a PDF document into the vector store
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional metadata for the document
            
        Returns:
            Number of chunks added
        """
        logger.info(f"Ingesting PDF: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path}")
            return 0
        
        # Chunk text
        chunks = self.chunk_text(text)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = [self.embed_text(chunk) for chunk in chunks]
        
        # Prepare metadata
        filename = Path(pdf_path).name
        doc_metadata = metadata or {}
        doc_metadata['source'] = filename
        doc_metadata['source_path'] = pdf_path
        
        # Generate IDs
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        
        # Add metadata to each chunk
        metadatas = [
            {**doc_metadata, 'chunk_id': i, 'total_chunks': len(chunks)}
            for i in range(len(chunks))
        ]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✓ Added {len(chunks)} chunks from {filename}")
        return len(chunks)
    
    def ingest_text(self, text: str, doc_id: str, metadata: Optional[Dict] = None) -> int:
        """
        Ingest plain text into the vector store
        
        Args:
            text: Text content
            doc_id: Unique identifier for the document
            metadata: Optional metadata
            
        Returns:
            Number of chunks added
        """
        logger.info(f"Ingesting text document: {doc_id}")
        
        # Chunk text
        chunks = self.chunk_text(text)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = [self.embed_text(chunk) for chunk in chunks]
        
        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata['source'] = doc_id
        
        # Generate IDs
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Add metadata to each chunk
        metadatas = [
            {**doc_metadata, 'chunk_id': i, 'total_chunks': len(chunks)}
            for i in range(len(chunks))
        ]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✓ Added {len(chunks)} chunks from {doc_id}")
        return len(chunks)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of results with documents, metadata, and scores
        """
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'persist_directory': self.persist_directory
        }
    
    def clear(self):
        """Clear all documents from the collection"""
        logger.warning("Clearing all documents from vector store")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Insurance policy documents"}
        )
        logger.info("✓ Collection cleared")


if __name__ == "__main__":
    # Test the vector store
    logging.basicConfig(level=logging.INFO)
    
    store = PolicyVectorStore()
    print("\n📊 Vector Store Stats:")
    print(store.get_stats())
