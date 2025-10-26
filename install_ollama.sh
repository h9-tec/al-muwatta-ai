#!/bin/bash

echo "======================================"
echo "🦙 Installing Ollama for Al-Muwatta"
echo "======================================"
echo ""

# Install Ollama
echo "📥 Step 1: Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "✅ Ollama installed!"
echo ""

# Install Python client
echo "📦 Step 2: Installing Ollama Python client..."
cd "$(dirname "$0")"
source venv/bin/activate
pip install ollama

echo ""
echo "✅ Python client installed!"
echo ""

# Pull recommended model
echo "📥 Step 3: Downloading Qwen2.5:7b (Arabic-optimized model)..."
echo "This may take 5-10 minutes (4.7GB download)..."
ollama pull qwen2.5:7b

echo ""
echo "======================================"
echo "✨ Ollama Setup Complete!"
echo "======================================"
echo ""
echo "🎯 Model Downloaded: qwen2.5:7b"
echo "💾 Size: ~4.7GB"
echo "🌍 Languages: Arabic, English, 50+"
echo ""
echo "🧪 Test it:"
echo "  ollama run qwen2.5:7b 'ما هو الإسلام؟'"
echo ""
echo "🚀 Start Ollama server:"
echo "  ollama serve"
echo ""
echo "======================================"

