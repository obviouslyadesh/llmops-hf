---
title: LLMOps Platform
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# LLMOps Platform ⚡

> A production-grade Retrieval-Augmented Generation (RAG) system — upload documents, ask questions, get AI-powered answers grounded in your own data.

---

## 📋 Problem Statement

Large Language Models (LLMs) are powerful, but they have a fundamental limitation: they only know what they were trained on. When you need answers from your own documents — internal knowledge bases, research papers, legal documents — a plain LLM falls short.

**RAG (Retrieval-Augmented Generation)** solves this by:
1. **Retrieving** relevant information from your documents
2. **Augmenting** the LLM prompt with that context
3. **Generating** answers grounded in your data — reducing hallucination

This platform provides a complete, production-ready RAG system with monitoring, evaluation, and observability built in.

---

## ✨ Key Features

- **📄 Multi-format Document Ingestion** — Upload PDF, TXT, and DOCX files
- **🧠 Smart Chunking** — Split documents into optimized chunks for retrieval
- **🔍 Vector Search** — Semantic search via Qdrant vector database (COSINE similarity)
- **⚡ Optional Reranking** — Cross-encoder reranking for improved answer quality
- **🤖 Dual LLM Support** — Choose between Groq (default) and Gemini
- **📡 Real-time Streaming** — SSE-based token streaming for responsive UI
- **📊 Comprehensive Monitoring** — Prometheus metrics + Grafana dashboards
- **🔍 LLM Tracing** — Full request tracing with Langfuse
- **📈 Evaluation Pipeline** — RAGAS-based automated quality assessment
- **🐳 Docker Orchestration** — Single-command full-stack deployment
- **🔐 API Authentication** — Optional API key middleware

---

## 🏗️ Architecture Overview

```

                    Upload
                        ↓
                Document Processor
                        ↓
                    Chunker
                        ↓
                Embedding Service
                        ↓
                      Qdrant
                        ↓
                    Question
                        ↓
                    Embedding
                        ↓
                    Retriever
                        ↓
                    Reranker
                        ↓
                    Prompt Builder
                        ↓
                    Groq/Gemini
                        ↓
                    Streaming Response
                        ↓
                    Langfuse
                        ↓
                    Prometheus
                        ↓
                    Grafana
```


---

## Demo

### Homepage & Document Upload
![Upload](images/Homepage.png)

### Chat Interface
![Chat](images/Chat.png)

### Langfuse Tracing
![Tracing](images/Langfuse.pngpng)

### Grafana Dashboard 1
![Grafana](images/Grafana%201.png)

### Grafana Dashboard 2
![Grafana](images/Grafana%202.png)

### Prometheus Metrics
![Metrics](images/Prometheus.png)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended)
- API key for Groq or Gemini

### 1. Clone & Setup

```bash
git clone <repo-url>
cd llmops-hf-pp

# Copy environment file
cp .env.example .env

# Run setup
bash setup.sh
```

### 2. Configure API Keys

Edit `.env` with your API keys:

```env
# At least one of these is required:
GEMINI_API_KEY="your-gemini-key"
GROQ_API_KEY="your-groq-key"

# LLM provider: "groq" (default) or "gemini"
LLM_PROVIDER="groq"
```

### 3. Run with Docker Compose

```bash
docker compose up --build -d
```

### 4. Open the App

| Service | URL |
|---|---|
| Web UI | http://localhost:7860 |
| API Docs | http://localhost:7860/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

---

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_NAME` | Yes | — | Application name |
| `GEMINI_API_KEY` | Yes\* | — | Google Gemini API key |
| `GROQ_API_KEY` | Yes\* | — | Groq API key |
| `LLM_PROVIDER` | No | `groq` | LLM provider selection |
| `QDRANT_URL` | Yes | `http://localhost:6333` | Qdrant server URL |
| `QDRANT_API_KEY` | No | — | Qdrant Cloud API key |
| `API_KEY` | No | — | API authentication key |
| `LANGFUSE_PUBLIC_KEY` | No | — | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | No | — | Langfuse secret key |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse host |

*\*At least one LLM API key required.*

---

## 📡 API Summary

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/upload` | POST | Upload document (PDF, TXT, DOCX) |
| `/chat` | POST | Ask a question (non-streaming) |
| `/chat/stream` | POST | Ask a question (SSE streaming) |
| `/search` | POST | Search documents |
| `/metrics` | GET | Prometheus metrics |


---

## 📁 Project Structure

```
app/                  # Application source code
├── api/routes/       # FastAPI route handlers
├── core/             # Config, models, middleware, logging
├── monitoring/       # Prometheus metrics definitions
├── services/         # Business logic (RAG, embedding, LLMs, etc.)
├── static/           # Frontend HTML/JS/CSS
└── main.py           # Application entry point

tests/                # Test suite
evaluation/           # RAGAS evaluation scripts
monitoring/           # Prometheus & Grafana config
```


---

## 📊 Evaluation

```bash
# Baseline evaluation (no reranking)
python3 evaluation/run_eval.py

# Reranked evaluation
python3 evaluation/run_eval_reranked.py
```


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/ -v`)
4. Run lint (`ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 🛡️ License

This project is licensed under the MIT License — see the [LICENSE](../LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework
- [Qdrant](https://qdrant.tech/) — Vector database
- [sentence-transformers](https://www.sbert.net/) — Embedding models
- [Groq](https://groq.com/) — LLM inference
- [Google Gemini](https://deepmind.google/technologies/gemini/) — LLM inference
- [Langfuse](https://langfuse.com/) — LLM observability
- [Prometheus](https://prometheus.io/) — Metrics
- [Grafana](https://grafana.com/) — Visualization
- [RAGAS](https://docs.ragas.io/) — RAG evaluation
