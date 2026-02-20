@echo off

:: Start FastAPI server
echo starting HellowBot FastAPI server...
start "" uvicorn main:app --reload --port 8000


:: Start HellowBot ui
echo starting HellowBot UI...
cd C:\Users\alex\Desktop\Sir Val AI\prontend
start "" python -m http.server 3000 


:: Start ollama local server (pedeng ma set ollama post via $env:OLLAMA_HOST="0.0.0.0:12345" sa powershell)
echo starting Ollama local server...
set OLLAMA_HOST=0.0.0.0:12345
start "" ollama serve 


:: start ngrok to expose the HellowBot UI
echo starting hellowbot UI via ngrok
start "" ngrok http 3000   


echo all servers started. Press any key to exit...
