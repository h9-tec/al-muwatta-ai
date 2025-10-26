#!/usr/bin/env python3
"""
Test Ollama Integration with Al-Muwatta

This script tests local LLM using Ollama.
"""

import asyncio
from loguru import logger

try:
    from src.services.ollama_service import OllamaService
except ImportError:
    print("❌ Ollama service not found")
    print("Make sure ollama_service.py exists")
    exit(1)


async def test_ollama():
    """Test Ollama with Arabic and English."""
    
    print("\n" + "="*60)
    print("🦙 Testing Ollama Local LLM")
    print("="*60 + "\n")

    try:
        # Initialize service
        print("🔧 Step 1: Initializing Ollama service...")
        service = OllamaService(model="qwen2.5:7b")
        print("✅ Service initialized\n")

        # Test 1: English question
        print("📝 Test 1: English Islamic question")
        print("Question: What are the five pillars of Islam?")
        print("Generating response...")
        
        english_response = await service.generate_content(
            "What are the five pillars of Islam? Be concise.",
            temperature=0.5,
            max_tokens=300,
        )
        
        if english_response:
            print(f"\n✅ Response:\n{english_response}\n")
        else:
            print("❌ No response\n")

        # Test 2: Arabic question
        print("-" * 60)
        print("📝 Test 2: Arabic Islamic question")
        print("Question: ما هي أركان الإسلام؟")
        print("Generating response...")
        
        arabic_response = await service.generate_content(
            "ما هي أركان الإسلام الخمسة؟ أجب بشكل مختصر.",
            temperature=0.5,
            max_tokens=300,
        )
        
        if arabic_response:
            print(f"\n✅ Response:\n{arabic_response}\n")
        else:
            print("❌ No response\n")

        # Test 3: List available models
        print("-" * 60)
        print("📊 Available Ollama models:")
        models = service.list_models()
        for model in models:
            print(f"  • {model}")

        print("\n" + "="*60)
        print("✨ Ollama Testing Complete!")
        print("="*60)
        print("\n🎯 Ollama is working with Al-Muwatta!")
        print("You can now use it instead of Google Gemini\n")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure:")
        print("  1. Ollama is installed: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Ollama server is running: ollama serve")
        print("  3. Model is downloaded: ollama pull qwen2.5:7b")
        print("  4. Python client installed: pip install ollama\n")


if __name__ == "__main__":
    asyncio.run(test_ollama())

