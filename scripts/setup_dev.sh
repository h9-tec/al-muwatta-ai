#!/bin/bash
# Development Environment Setup Script for Al-Muwatta
# This script automates the complete development environment setup

set -e  # Exit on error

echo "🚀 Al-Muwatta Development Environment Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Python $required_version or higher required. Found: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python version: $python_version${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing production dependencies..."
pip install -r requirements.txt --quiet

echo "📥 Installing development dependencies..."
pip install -r requirements-dev.txt --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install
echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please update .env with your API keys${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example not found, skipping .env creation${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create logs directory
if [ ! -d "logs" ]; then
    echo "📁 Creating logs directory..."
    mkdir -p logs
    echo -e "${GREEN}✅ Logs directory created${NC}"
fi

# Initialize database (if script exists)
if [ -f "initialize_rag.py" ]; then
    echo "🗄️  Initializing RAG database..."
    python initialize_rag.py
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠️  initialize_rag.py not found, skipping database initialization${NC}"
fi

# Run linting
echo "🔍 Running code quality checks..."
echo "  - Ruff linting..."
ruff check src/ tests/ --fix || true
echo "  - Ruff formatting..."
ruff format src/ tests/ || true
echo -e "${GREEN}✅ Code formatted${NC}"

# Run type checking
echo "🔍 Running type checks..."
mypy src/ --ignore-missing-imports --no-strict-optional || true
echo -e "${GREEN}✅ Type checking complete${NC}"

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --cov=src --cov-report=term-missing || true
echo -e "${GREEN}✅ Tests complete${NC}"

echo ""
echo "============================================"
echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo ""
echo "📚 Next steps:"
echo "  1. Update .env with your API keys"
echo "  2. Run 'source venv/bin/activate' to activate the environment"
echo "  3. Run 'python run.py' to start the backend"
echo "  4. Run 'cd frontend && npm install && npm run dev' to start the frontend"
echo ""
echo "🔧 Useful commands:"
echo "  - pytest tests/ -v                    # Run tests"
echo "  - ruff check src/                     # Lint code"
echo "  - mypy src/                           # Type check"
echo "  - pre-commit run --all-files          # Run all pre-commit hooks"
echo ""

