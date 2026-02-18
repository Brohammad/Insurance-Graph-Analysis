"""
Ingest insurance policy documents into ChromaDB vector store
"""

import os
import logging
from pathlib import Path
from vector_store import PolicyVectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def ingest_policy_documents():
    """Ingest all policy documents from policy_documents directory"""
    
    print("\n" + "="*70)
    print("📚 Policy Document Ingestion - ChromaDB Vector Store")
    print("="*70 + "\n")
    
    # Initialize vector store
    store = PolicyVectorStore(persist_directory="./chroma_db")
    
    # Get policy documents directory
    docs_dir = Path("policy_documents")
    
    if not docs_dir.exists():
        logger.error(f"Directory {docs_dir} does not exist")
        return
    
    # Find all text and PDF files
    text_files = list(docs_dir.glob("*.txt"))
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    total_chunks = 0
    
    # Ingest text files
    for file_path in text_files:
        print(f"\n📄 Processing: {file_path.name}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract metadata from filename
            metadata = {
                'filename': file_path.name,
                'document_type': 'policy',
                'format': 'text'
            }
            
            # Add type-specific metadata
            if 'comprehensive' in file_path.name.lower():
                metadata['policy_type'] = 'comprehensive_health'
                metadata['policy_number'] = 'POL001'
            elif 'critical' in file_path.name.lower():
                metadata['policy_type'] = 'critical_illness_rider'
                metadata['rider_code'] = 'CIR-2025'
            
            chunks = store.ingest_text(text, file_path.stem, metadata)
            total_chunks += chunks
            print(f"   ✓ Added {chunks} chunks")
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
    
    # Ingest PDF files
    for file_path in pdf_files:
        print(f"\n📄 Processing: {file_path.name}")
        try:
            metadata = {
                'filename': file_path.name,
                'document_type': 'policy',
                'format': 'pdf'
            }
            
            chunks = store.ingest_pdf(str(file_path), metadata)
            total_chunks += chunks
            print(f"   ✓ Added {chunks} chunks")
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
    
    # Print statistics
    print("\n" + "="*70)
    print("📊 Ingestion Complete!")
    print("="*70)
    
    stats = store.get_stats()
    print(f"\n✓ Collection: {stats['collection_name']}")
    print(f"✓ Total chunks: {stats['total_chunks']}")
    print(f"✓ Storage: {stats['persist_directory']}")
    
    print(f"\n✓ Processed {len(text_files)} text files")
    print(f"✓ Processed {len(pdf_files)} PDF files")
    print(f"✓ Total chunks added: {total_chunks}")
    
    # Test search
    print("\n" + "="*70)
    print("🔍 Testing Search Functionality")
    print("="*70 + "\n")
    
    test_queries = [
        "Is diabetes covered in the policy?",
        "What are the exclusions for critical illness?",
        "How much is the maternity benefit?",
        "Which hospitals are in the network?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        results = store.search(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n   Result {i} (distance: {result['distance']:.4f}):")
                print(f"   Source: {result['metadata'].get('filename', 'Unknown')}")
                snippet = result['document'][:150] + "..." if len(result['document']) > 150 else result['document']
                print(f"   Snippet: {snippet}")
        else:
            print("   No results found")
    
    print("\n" + "="*70)
    print("✅ Policy documents ingested successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    ingest_policy_documents()
