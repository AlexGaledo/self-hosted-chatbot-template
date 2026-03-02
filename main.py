import json
import os
import datetime
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Load persona data
with open(os.path.join(os.path.dirname(__file__), "persona.json"), "r") as f:
    persona_data = json.load(f)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to frontend folder
frontend_path = os.path.join(os.path.dirname(__file__), "prontend")  # intentional

# Mount static files
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Pydantic model for chat requests
class ChatRequest(BaseModel):
    message: str
    session_id: str = None # type: ignore

# In-memory session storage
sessions = {}

# Ollama server
ollama_server = "http://127.0.0.1:11434"

@app.get("/")
def serve_ui():
    """Serve the frontend UI"""
    return FileResponse(os.path.join(frontend_path, "index.html"))

def get_relevant_persona_info(user_message: str):
    """Return only personas that match keywords in the user's message"""
    relevant = []
    msg_lower = user_message.lower()
    for arcana, personas in persona_data.get("personas_by_arcana", {}).items():
        for persona in personas:
            if persona["name"].lower() in msg_lower or arcana.lower() in msg_lower:
                relevant.append(persona)
    return relevant

@app.post("/chat")
def chat(req: ChatRequest):
    # Determine session key (avoid mixing None)
    session_key = req.session_id or "default"

    # Initialize session history if missing
    if session_key not in sessions:
        sessions[session_key] = []

    history = sessions[session_key]

    # Add user message
    timestamp = datetime.datetime.now().isoformat()
    history.append({"role": "user", "content": req.message, "timestamp": timestamp})

    # Get relevant personas as JSON
    relevant_personas = get_relevant_persona_info(req.message)
    relevant_personas_json = relevant_personas if relevant_personas else []

    # Build conversation for Ollama
    conversation = ""
    for msg in history:
        conversation += f"{msg['role']}: {msg['content']}\n"
    conversation += "assistant:"

    # System prompt with JSON feed
    system_prompt = f"""
You are a nerdy, fun assistant obsessed with Persona 3.
- Only respond with info related to Persona 3.
- Use psychological concepts, Tarot, Arcana, and Carl Jung theories.
- If nothing matches, reply: "Sorry, I can only talk about Persona 3!"
- If user greets, reply with: "Hello! I'm your Persona 3 assistant. How can I help you today?"
- Here is the JSON of relevant personas for this query (feed it directly to your reasoning, don't ignore it):
{json.dumps(relevant_personas_json)}
Always respond conversationally with emojis and gifs if appropriate.
"""

    # Prepare payload
    payload = {
        "model": "qwen2:7b",
        "system": system_prompt,
        "prompt": conversation,
        "stream": False
    }

    # Call Ollama
    try:
        response = requests.post(f"{ollama_server}/api/generate", json=payload)
        data = response.json()
        bot_reply = data.get("response", "").strip()
    except Exception as e:
        bot_reply = f"Error contacting Ollama: {e}"

    # Add bot reply to history
    history.append({"role": "bot", "content": bot_reply, "timestamp": datetime.datetime.now().isoformat()})

    # Save updated history
    sessions[session_key] = history

    return {"user_message": req.message, "ollama_response": bot_reply, "history": history}