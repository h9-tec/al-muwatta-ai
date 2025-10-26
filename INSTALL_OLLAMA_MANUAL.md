# Install Ollama Manually

Since Ollama requires sudo, please run this yourself:

## Step 1: Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2: Start Ollama Service

```bash
ollama serve
```

Keep this running in a terminal.

## Step 3: Download a Model (in new terminal)

### Recommended: Qwen2.5 (Best for Arabic)
```bash
ollama pull qwen2.5:7b
```

### Alternatives:
```bash
# Smaller, faster (1GB)
ollama pull qwen2.5:0.5b

# Larger, better quality (8GB)  
ollama pull qwen2.5:14b

# Llama 3.1 (good multilingual)
ollama pull llama3.1:8b
```

## Step 4: Install Python Client

```bash
cd /home/hesham/hadith
source venv/bin/activate
pip install ollama
```

## Step 5: Test

```bash
python test_ollama.py
```

## Step 6: Use in Al-Muwatta

1. Click ⚙️ Settings button in the app
2. Select "Ollama (Local)"
3. Click "Fetch Available Models"
4. Choose your downloaded model
5. Click "Test Connection"
6. Click "Save Settings"

✅ Now using local LLM! No API costs!
