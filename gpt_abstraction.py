import openai
import requests
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from wrapt_timeout_decorator import timeout
import json

from config import OLLAMA_EMBEDDING_URL, OLLAMA_MODEL, OLLAMA_GENERATE_URL

# Set keys via environment or elsewhere
openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@timeout(60)
def engine_abstraction(model: str, prompt, messages=None, temperature=1.0, max_tokens=512):
    if model.startswith("gpt-"):
        return _call_openai(model, messages or _format_openai_messages(prompt), temperature, max_tokens)
    elif model.startswith("claude"):
        return _call_claude(model, prompt, temperature, max_tokens)
    elif model == "mistral" or model == "local":
        return _call_mistral_local(prompt, temperature, max_tokens)
    else:
        raise ValueError(f"Model {model} is not supported")

def _format_openai_messages(prompt):
    if isinstance(prompt, str):
        return [{"role": "user", "content": prompt}]
    return prompt

def _call_openai(model, messages, temperature, max_tokens):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message["content"]

def _call_claude(model, prompt, temperature, max_tokens):
    response = anthropic_client.completions.create(
        model=model,
        prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
        max_tokens_to_sample=max_tokens,
        temperature=temperature
    )
    return response.completion

def _call_mistral_local(prompt, temperature, max_tokens):
    url = OLLAMA_GENERATE_URL
    
    # Convert message list into a flat prompt
    if isinstance(prompt, list):
        
        memory_text = []
        for m in prompt:
            if m["role"] == "memory":
                memory_text.append(m["content"])
            elif m["role"] == "user":
                memory_text.append(f"User: {m['content']}")
            elif m["role"] == "assistant":
                memory_text.append(f"Assistant: {m['content']}")
        flat_prompt = "\n".join(memory_text)
    else:
        flat_prompt = prompt

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": flat_prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json().get("response", "").strip()

