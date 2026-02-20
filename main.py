from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Enable CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to frontend folder
frontend_path = os.path.join(os.path.dirname(__file__), "prontend")

# Mount the folder so all CSS/JS/images are accessible
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Pydantic model for chat request
class ChatRequest(BaseModel):
    message: str

ollama_server = "http://127.0.0.1:11434"  # default Ollama

@app.get("/")
def serve_ui():
    # Serve index.html
    return FileResponse(os.path.join(frontend_path, "index.html"))


#chatbot endpoint
@app.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message
    payload = {
        "model": "phi",
        "prompt": user_message,
        "stream": False
    }
    try:
        response = requests.post(f"{ollama_server}/api/generate", json=payload)
        data = response.json()
        ollama_reply = data.get("response", "").strip()
    except Exception as e:
        ollama_reply = f"Error contacting Ollama: {e}"
    return {"user_message": user_message, "ollama_response": ollama_reply}