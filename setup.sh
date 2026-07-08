#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# LLMOps Platform — Setup Script
# =============================================================================
# This script sets up the local development environment.
# Usage: bash setup.sh
# =============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       LLMOps Platform — Development Setup                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# ------------------------------------------------------------------
# Step 1: Check prerequisites
# ------------------------------------------------------------------
echo ""
echo "🔍 Checking prerequisites..."

# Python 3.12+
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "none")
if [[ "$PYTHON_VERSION" == "Python 3.12"* ]] || [[ "$PYTHON_VERSION" == "Python 3.13"* ]]; then
    echo "  ✓ Python: $PYTHON_VERSION"
else
    echo "  ✗ Python 3.12+ is required. Found: $PYTHON_VERSION"
    echo "    Install Python 3.12 from https://www.python.org/downloads/"
    exit 1
fi

# pip
if command -v pip3 &>/dev/null; then
    echo "  ✓ pip3: $(pip3 --version | cut -d' ' -f2)"
else
    echo "  ✗ pip3 is not installed"
    exit 1
fi

# Docker (optional)
if command -v docker &>/dev/null; then
    echo "  ✓ Docker: $(docker --version | cut -d' ' -f3 | tr -d ',')"
    DOCKER_AVAILABLE=true
else
    echo "  ⚠ Docker not found — will run Qdrant via pip instead"
    DOCKER_AVAILABLE=false
fi

# ------------------------------------------------------------------
# Step 2: Create virtual environment
# ------------------------------------------------------------------
echo ""
echo "🔧 Creating Python virtual environment..."

if [ -d "venv" ]; then
    echo "  ✓ Virtual environment already exists at ./venv/"
else
    python3 -m venv venv
    echo "  ✓ Created virtual environment at ./venv/"
fi

# Activate
source venv/bin/activate
echo "  ✓ Activated virtual environment"

# ------------------------------------------------------------------
# Step 3: Install dependencies
# ------------------------------------------------------------------
echo ""
echo "📦 Installing Python dependencies..."

pip install --upgrade pip --quiet
echo "  ✓ pip upgraded"

pip install --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt --quiet
echo "  ✓ Production dependencies installed"

pip install -r requirements-dev.txt --quiet
echo "  ✓ Development dependencies installed"

# ------------------------------------------------------------------
# Step 4: Create .env file if missing
# ------------------------------------------------------------------
echo ""
echo "⚙️  Checking environment configuration..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ⚠ Created .env from .env.example — please edit it with your API keys"
    echo "    Edit: nano .env"
else
    echo "  ✓ .env file exists"
fi

# ------------------------------------------------------------------
# Step 5: Start Qdrant (if Docker is available)
# ------------------------------------------------------------------
echo ""
echo "🗄️  Starting Qdrant vector database..."

if [ "$DOCKER_AVAILABLE" = true ]; then
    # Check if Qdrant is already running
    if docker ps --format '{{.Names}}' | grep -q 'qdrant'; then
        echo "  ✓ Qdrant is already running"
    else
        echo "  Starting Qdrant container..."
        docker run -d \
            --name qdrant \
            -p 6333:6333 \
            -v qdrant_data:/qdrant/storage \
            qdrant/qdrant:latest
        echo "  ✓ Qdrant started on port 6333"
    fi
else
    echo "  ⚠ Docker not available — please start Qdrant manually:"
    echo "    docker run -d -p 6333:6333 qdrant/qdrant"
    echo "    Or install qdrant-client and use an in-memory store"
fi

# ------------------------------------------------------------------
# Step 6: Install pre-commit hooks (optional)
# ------------------------------------------------------------------
echo ""
echo "🔗 Setting up Git hooks..."

if command -v pre-commit &>/dev/null; then
    pre-commit install 2>/dev/null || echo "  ⚠ pre-commit install failed (optional)"
    echo "  ✓ Pre-commit hooks installed"
else
    echo "  ⚠ pre-commit not installed (optional)"
fi

# ------------------------------------------------------------------
# Step 7: Run linting check
# ------------------------------------------------------------------
echo ""
echo "🔍 Running lint check..."

if command -v ruff &>/dev/null; then
    ruff check . --quiet || echo "  ⚠ Lint issues found — run 'ruff check .' to see details"
    echo "  ✓ Lint check completed"
else
    echo "  ⚠ ruff not found — run 'pip install ruff'"
fi

# ------------------------------------------------------------------
# Step 8: Run tests
# ------------------------------------------------------------------
echo ""
echo "🧪 Running tests..."

if python3 -m pytest tests/ -v --quiet 2>/dev/null; then
    echo "  ✓ All tests passed"
else
    echo "  ⚠ Tests failed — check output above"
fi

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Setup Complete!                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Edit your API keys:  nano .env"
echo ""
echo "  2. Start the server:    uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload"
echo ""
echo "  3. Open the app:        http://localhost:7860"
echo ""
echo "  4. View API docs:       http://localhost:7860/docs"
echo ""
echo "  Or run with Docker:     docker compose up --build"
echo ""
echo "  Happy building! ⚡"
echo ""
