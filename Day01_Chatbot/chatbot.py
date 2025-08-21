import os
import requests
import json
from dotenv import load_dotenv

# Load API keys
load_dotenv()
HF_API_KEY = os.getenv("HuggingFaceAPIKey")
GROQ_API_KEY = os.getenv("GroqAPIKey")

# System prompt
SYSTEM_PROMPT = "You are Neo. Always introduce yourself as Neo when asked your name."
CHAT_HISTORY_FILE = "chat_history.json"

# ✅ Centralized list of name phrases
NAME_PHRASES = [
    "your name", "what's your name", "whats your name", "what is your name",
    "tell me your name", "who are you", "who am i talking to", "who is this",
    "who are u", "who r you", "who r u", "ur name", "identity"
]

# Save conversation
def save_conversation(user_input, bot_response):
    chat_entry = {"user": user_input, "bot": bot_response}
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []
    except Exception:
        history = []
    history.append(chat_entry)
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# HuggingFace API
def query_huggingface(question):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Answer the following question clearly:\nQuestion: {question}\nAnswer:"
    payload = {"inputs": prompt}
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"].strip()
    elif "error" in result:
        raise Exception(result["error"])
    return "Sorry, I couldn’t understand that."

# Groq API
def query_groq(question):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

# Chatbot main logic
def chatbot_answer(user_input):
    lowered = user_input.lower().strip()

    # 🔥 Rule override for name
    if any(phrase in lowered for phrase in NAME_PHRASES):
        return "I am Neo, your AI assistant. I'm here to help you with anything you want to know!"

    # Otherwise, try APIs
    try:
        return query_huggingface(user_input)
    except Exception:
        return query_groq(user_input)

if __name__ == "__main__":
    print("🤖 Chatbot ready! Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Bot: Thank you for chatting with me! Have a wonderful day! 👋")
            break

        answer = chatbot_answer(user_input)
        print("Bot:", answer)

        save_conversation(user_input, answer)
