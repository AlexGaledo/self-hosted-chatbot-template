@echo off

:: Start FastAPI server
echo starting HellowBot FastAPI server...
start "" uvicorn main:app --reload --host 0.0.0.0 --port 8000


:: Start ollama local server (pedeng ma set ollama post via $env:OLLAMA_HOST="0.0.0.0:12345" sa powershell)
echo starting Ollama local server...
start "" ollama serve 


:: start ngrok to expose the HellowBot UI
echo starting hellowbot UI via ngrok
start "" ngrok http 8000   


echo all servers started. Press any key to exit...
