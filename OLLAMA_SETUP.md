# Running Al-Muwatta Locally with Ollama

## Install Ollama

```bash
# Install Ollama on Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from: https://ollama.com/download
```

## Download Arabic-Capable Models

### Option 1: Qwen2.5 (Best for Arabic)
```bash
# 7B model (Recommended - good balance)
ollama pull qwen2.5:7b

# 14B model (Better quality, needs more RAM)
ollama pull qwen2.5:14b

# 0.5B model (Very fast, testing only)
ollama pull qwen2.5:0.5b
```

### Option 2: Llama 3.1 (Good multilingual)
```bash
ollama pull llama3.1:8b
```

### Option 3: Mistral (Fast)
```bash
ollama pull mistral:7b
```

## Test the Model

```bash
# Start Ollama service
ollama serve &

# Test with Arabic
ollama run qwen2.5:7b "ما هو الإسلام؟"

# Test with English
ollama run qwen2.5:7b "What is Islam?"
```

## Integration with Al-Muwatta

Install Python client:
```bash
cd /home/hesham/hadith
source venv/bin/activate
pip install ollama
```

## Switch from Gemini to Ollama

Set in config or environment:
```bash
export USE_LOCAL_LLM=true
export OLLAMA_MODEL=qwen2.5:7b
```

## Performance Comparison

| Model | RAM Needed | Speed | Arabic Quality |
|-------|------------|-------|----------------|
| Qwen2.5:0.5b | 1GB | ⚡⚡⚡ | ⭐⭐ |
| Qwen2.5:7b | 8GB | ⚡⚡ | ⭐⭐⭐⭐ |
| Qwen2.5:14b | 16GB | ⚡ | ⭐⭐⭐⭐⭐ |
| Llama3.1:8b | 8GB | ⚡⚡ | ⭐⭐⭐ |

**Recommended for Al-Muwatta**: Qwen2.5:7b

