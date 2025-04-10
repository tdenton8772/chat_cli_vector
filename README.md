#chat_cli

# Lightweight RAG CLI (No Vector Store)

This repo contains a minimal Retrieval-Augmented Generation (RAG) system built with:

- Python CLI interface
- Redis for memory
- Mistral running locally via Ollama
- No vector store, no embedding pipeline
- Simplified context retention using NLP

## Requirements

- [Docker](https://www.docker.com/)
- [Ollama](https://ollama.com/) installed on your host (for running Mistral)
- Python 3.11+ if you want to run anything outside the container

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tdenton8772/chat_cli
cd chat-cli
```

2. Build the Docker containers
```bash
docker compose build
```

This sets up:

A Python container for the CLI

Redis for memory

Ollama for serving the Mistral model

Persistent volumes for Redis and model data

3. Pull the Mistral model (important!)
This step is required before using the CLI with Mistral.

```bash
ollama pull mistral
```
Do this from the cli of the ollama container. The mistral llm will be stored in a resuable volume.

4. Run the CLI interactively
```bash
./run.sh
```

You'll be prompted to select a model and either start a new conversation or continue an existing one.

### Memory Handling
Every user-assistant exchange is minified using NLP (stopword removal, stemming, lemmatization)

Memory is stored in Redis as compressed dialog summaries

On each new prompt, the last 20 memory entries are used to restore context

### CLI Commands
You can use these slash commands while chatting:

Command	Description
```bash
/list	Show all saved conversations
/switch <id>	Switch to another conversation
/delete <id>	Delete a conversation
/recap	View compressed memory for current session
/help	Show all commands
exit / quit	End the session
```

### Project Structure
```bash
.
├── chat_cli.py           # Main CLI
├── gpt_abstraction.py    # Model switcher (Mistral, OpenAI, Claude)
├── memory_summarizer.py  # NLP minifier
├── entrypoint.sh         # CLI startup
├── run.sh                # Host launch script
├── docker-compose.yml
├── Dockerfile
```

🧪 Note on Other Models
This repo supports Claude and OpenAI models through abstraction, but only Mistral via Ollama is fully tested and configured in this implementation. You’re free to extend or replace models via gpt_abstraction.py.

