#!/usr/bin/env python3
"""
Initialize Maliki Fiqh RAG Knowledge Base

This script sets up the vector database with Maliki fiqh texts.
"""

import asyncio
from loguru import logger

from src.services.rag_service import MalikiFiqhRAG


async def main():
    """Initialize the RAG knowledge base."""
    print("\n" + "="*60)
    print("🌟 Initializing Maliki Fiqh RAG Knowledge Base")
    print("="*60 + "\n")

    try:
        # Initialize RAG system
        print("📚 Step 1: Loading embedding model...")
        rag = MalikiFiqhRAG()
        print("✅ Embedding model loaded\n")

        # Initialize knowledge base
        print("📖 Step 2: Adding Maliki fiqh texts to vector database...")
        await rag.initialize_knowledge_base(force_reload=True)
        print("✅ Knowledge base populated\n")

        # Get statistics
        print("📊 Step 3: Checking statistics...")
        stats = rag.get_statistics()
        print(f"✅ Total documents: {stats['total_documents']}")
        print(f"✅ Collection: {stats['collection_name']}")
        print(f"✅ Model: {stats['embedding_model']}")
        print(f"✅ Status: {stats['status']}\n")

        # Test search
        print("🔍 Step 4: Testing search functionality...")
        test_query = "What is the Maliki ruling on raising hands in prayer?"
        results = rag.search(test_query, n_results=2)

        if results:
            print(f"✅ Search test successful! Found {len(results)} results\n")
            print("Sample result:")
            print(f"  Topic: {results[0]['metadata']['topic']}")
            print(f"  Category: {results[0]['metadata']['category']}")
            print(f"  Text preview: {results[0]['text'][:150]}...\n")
        else:
            print("⚠️  No results found\n")

        print("="*60)
        print("✨ RAG System Ready!")
        print("="*60)
        print("\n🚀 The chatbot will now use Maliki fiqh knowledge")
        print("   to answer questions with authentic sources!\n")

    except Exception as e:
        logger.error(f"Error initializing RAG: {e}")
        print(f"\n❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())

