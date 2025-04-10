# chat_cli_vector

## Lightweight Hybrid RAG Chatbot (KV + Vector Memory)

This repo is a minimal Retrieval-Augmented Generation (RAG) system that combines both:

- Short-term memory using Redis (key-value)
- Long-term semantic memory using FAISS (vector search)
- Embeddings generated locally using Mistral via Ollama

---

### Key Features

- Python CLI interface for chatting with LLMs
- Memory summaries of user+assistant exchanges stored in Redis
- User inputs and summarized replies embedded and stored in FAISS
- Vector search for semantically relevant recall (even after a restart)
- Modular design via `gpt_abstraction.py` and `vector_store.py`
- All local, no external APIs required

---

## Requirements

- [Docker](https://www.docker.com/)
- [Ollama](https://ollama.com/) installed on your host (for running Mistral)
- Python 3.11+ if you want to run parts outside the container

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tdenton8772/chat_cli_vector
cd chat_cli_vector
```

### 2. Build the Containers

```bash
docker compose build
```

This sets up:
- A Python container for the CLI
- Redis for memory storage
- Ollama for embedding and model inference
- Persistent volumes for Redis and model data

---

### 3. Pull the Mistral Model

You need to pull mistral manually before running the CLI:

```bash
ollama pull mistral
```

This stores the model in a volume accessible to the containerized Ollama service.

---

### 4. Run the CLI

```bash
./run.sh
```

You'll be prompted to select a model and either start a new conversation or continue an existing one.


## Memory System

| Layer | Description|
| :---------- | :---------------------- |
| Redis (KV)	| Stores compressed memory summaries (last 5 by default)
| FAISS (Vector) |	Stores semantic memory for all user inputs + assistant summaries
| Embeddings	| Generated using Mistral via Ollama
| Persistence	| FAISS index is saved to disk and automatically restored

### CLI Commands

```bash
/list             Show all saved conversations
/switch <id>      Switch to another conversation
/delete <id>      Delete a conversation
/recap            View Redis-stored memory summaries
/vectors          View all stored FAISS memory entries
/help             Show this help menu
exit / quit       End the session
```

### Project Structure

```bash
.
├── chat_cli.py            # Main CLI loop
├── hybrid_memory.py       # Combines Redis + FAISS memory
├── vector_store.py        # FAISS wrapper with persistence
├── embedding.py           # Calls Mistral via Ollama for embeddings
├── gpt_abstraction.py     # Switches between Mistral / OpenAI / Claude
├── memory_summarizer.py   # NLP summarizer (used before storing in Redis)
├── config.py              # Model names, embedding dim, top_k, etc.
├── run.sh                 # Host launch script
├── entrypoint.sh          # CLI startup
├── docker-compose.yml
├── Dockerfile
```

---

Notes on Model Support
Fully tested: Mistral via Ollama

Claude + OpenAI supported via gpt_abstraction.py, but not tested in this setup

Easily swappable with your own backend model service

PRs and feedback welcome!