import os
import json
import redis

from embedding import get_embedding
from vector_store import FaissVectorStore
from memory_summarizer import summarize_exchange

from config import OLLAMA_EMBEDDING_URL, OLLAMA_MODEL, EMBEDDING_DIM

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MAX_HISTORY = 5

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

vector_store = FaissVectorStore(dim=EMBEDDING_DIM)

def load_kv_memory(conv_id):
    raw = r.get(f"convo:{conv_id}")
    return json.loads(raw) if raw else []

def save_to_kv(conv_id, role, content):
    key = f"convo:{conv_id}"
    history = load_kv_memory(conv_id)

    if role == "assistant" and len(history) > 0 and history[-1]["role"] == "user":
        user_input = history[-1]["content"]
        assistant_reply = content
        summary = summarize_exchange(user_input, assistant_reply)
        history.append({"role": "memory", "content": summary})

        # Store in vector store too
        try:
            embedding = get_embedding(summary)
            vector_store.add(summary, embedding, metadata={"conv_id": conv_id})
        except Exception as e:
            print("Vector embedding error:", e)

        # Optionally prune user+assistant messages
        history = [msg for msg in history if msg["role"] == "memory"]

    elif role == "user":
        history.append({"role": "user", "content": content})

    history = history[-MAX_HISTORY:]
    r.set(key, json.dumps(history))

def build_context(conv_id, user_input, top_k=4):
    history = load_kv_memory(conv_id)
    kv_memory = [m for m in history if m["role"] == "memory"]

    # Embed input and query vector store
    try:
        query_embedding = get_embedding(user_input)
        vector_hits = vector_store.search(query_embedding, top_k=top_k, conv_id=conv_id)

        # Filter out hits that match the input text exactly (or closely)
        vector_memory = []
        for hit in vector_hits:
            if hit["text"].strip().lower() == user_input.strip().lower():
                continue  # Skip echoing input
            vector_memory.append({"role": "memory", "content": hit["text"]})
        for memory in vector_memory:
            print(f" • {memory['content']}")
        vector_memory = [{"role": "memory", "content": hit["text"]} for hit in vector_hits]
    except Exception as e:
        print("Vector search error:", e)
        vector_memory = []

    return vector_memory + kv_memory + [{"role": "user", "content": user_input}]

def delete_conversation(conv_id):
    r.delete(f"convo:{conv_id}")

def save_message(conv_id, role, content):
    key = f"convo:{conv_id}"
    history = load_kv_memory(conv_id)

    # If this is the assistant replying to a previous user message, summarize both
    if role == "assistant" and len(history) > 0 and history[-1]["role"] == "user":
        user_input = history[-1]["content"]
        assistant_reply = content
        summary = summarize_exchange(user_input, assistant_reply)
        history.append({"role": "memory", "content": summary})

        # Store in vector store too
        try:
            embedding = get_embedding(summary)
            vector_store.add(text=summary, embedding=embedding, metadata={"conv_id": conv_id})
        except Exception as e:
            print("Vector embedding error:", e)

        history = [msg for msg in history if msg["role"] == "memory"]

    elif role == "user":
        history.append({"role": "user", "content": content})

        try:
            embedding = get_embedding(content)
            vector_store.add(text=content, embedding=embedding, metadata={
                "conv_id": conv_id,
                "source": "user"
            })
        except Exception as e:
            print("Vector embedding (user) error:", e)


    # Limit total entries (20 summaries ~= ~1000 tokens or less)
    history = history[-MAX_HISTORY:]
    r.set(key, json.dumps(history))
