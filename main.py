from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local Ollama API
ollama_server = "http://localhost:12345"

class ChatRequest(BaseModel):
    message: str

@app.get('/')
def index():
    return {"response": "HellowBot is running!"}

@app.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message

    payload = {
        "model": "phi",
        "prompt": user_message,
        "max_tokens": 150,
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{ollama_server}/v1/completions", json=payload)
        data = response.json()
        ollama_reply = data.get("choices", [{}])[0].get("text", "").strip()
    except Exception as e:
        ollama_reply = f"Error contacting Ollama: {e}"

    return {
        "user_message": user_message,
        "ollama_response": ollama_reply
    }