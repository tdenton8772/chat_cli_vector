import os
import uuid
import json
import redis
from gpt_abstraction import engine_abstraction

from hybrid_memory import save_message, build_context, vector_store

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MAX_HISTORY = 20

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

SUPPORTED_MODELS = ["gpt-3.5-turbo", "gpt-4", "claude-3-opus-20240229", "mistral"]

def get_conversation_list():
    keys = r.keys("convo:*")
    return [key.replace("convo:", "") for key in keys]

def load_conversation(conv_id):
    raw = r.get(f"convo:{conv_id}")
    return json.loads(raw) if raw else []

def choose_model():
    print("Available models:")
    for i, model in enumerate(SUPPORTED_MODELS, 1):
        print(f"{i}. {model}")
    choice = int(input("Choose a model [1-{}]: ".format(len(SUPPORTED_MODELS))))
    return SUPPORTED_MODELS[choice - 1]

def choose_conversation():
    conversations = get_conversation_list()

    if conversations:
        print("Available conversations:")
        for i, cid in enumerate(conversations, 1):
            print(f"{i}. {cid}")
        print(f"{len(conversations)+1}. Start a new conversation")

        choice = input("Select a conversation (number or name): ").strip()

        # Allow direct ID typing
        if choice in conversations:
            return choice

        # Try to parse as index
        try:
            idx = int(choice)
            if 1 <= idx <= len(conversations):
                return conversations[idx - 1]
        except ValueError:
            pass  # Not a number

    # Default: start new
    new_id = str(uuid.uuid4())
    print(f"Starting new conversation: {new_id}")
    return new_id


def chat_loop(model, conv_id):
    print(f"\n--- Chatting with `{model}` ---")
    print(f"Conversation ID: {conv_id}\n(Type '/help' for commands, 'exit' to quit)\n")

    while True:
        user_input = input("You: ").strip()

        # Handle slash commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            if cmd in ["/exit", "/quit"]:
                break
            elif cmd == "/help":
                print("""
Available commands:
/help                 Show this help message
/list                 List all saved conversations
/switch <id>          Switch to another conversation
/delete <id>          Delete a conversation
/exit or /quit        End the current session
""")
                continue

            elif cmd == "/list":
                print("Saved conversations:")
                for cid in get_conversation_list():
                    print(f" - {cid}")
                continue

            elif cmd == "/switch":
                if arg and arg in get_conversation_list():
                    conv_id = arg
                    print(f"Switched to conversation '{conv_id}'")
                    continue
                else:
                    print("Conversation ID not found.")
                    continue

            elif cmd == "/delete":
                if arg and arg in get_conversation_list():
                    confirm = input(f"Are you sure you want to delete '{arg}'? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        delete_conversation(arg)
                        if arg == conv_id:
                            print("Current conversation deleted. Starting new one.")
                            conv_id = str(uuid.uuid4())
                        continue
                    else:
                        print("Deletion canceled.")
                        continue
                else:
                    print("Conversation ID not found.")
                    continue
            elif cmd == "/recap":
                print(f"Conversation summary for '{conv_id}':\n")
                history = load_conversation(conv_id)
                for i, msg in enumerate(history):
                    if msg["role"] == "memory":
                        print(f"{i+1}. {msg['content']}")
                continue
            elif cmd == "/vectors":
                vector_store.debug_dump()
                continue
            else:
                print("Unknown command. Type /help for options.")
                continue
        else:    
            save_message(conv_id, "user", user_input)
            context = build_context(conv_id, user_input)
            try:
                response = engine_abstraction(model=model, prompt=context)
            except Exception as e:
                print("Error:", e)
                continue
            print("AI:", response)
            save_message(conv_id, "assistant", response)

        
def delete_conversation(conv_id):
    key = f"convo:{conv_id}"
    r.delete(key)
    print(f"Deleted conversation '{conv_id}'")

if __name__ == "__main__":
    model = choose_model()
    conversation_id = choose_conversation()
    chat_loop(model, conversation_id)
