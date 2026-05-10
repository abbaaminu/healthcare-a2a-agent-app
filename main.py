import os
import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI()

# Enable CORS for Prompt Opinion to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render needs this to return 200 OK to keep the app alive
@app.get("/")
async def health():
    return {"status": "alive", "service": "Healthcare Agent"}

@app.get("/.well-known/ai-agent.json")
@app.get("/ai-agent.json")
async def agent_card():
    return {
        "name": "Healthcare A2A Risk Analyzer",
        "description": "Clinical decision support for BP and Cardiovascular risk",
        "version": "2.0.0",
        "url": "https://healthcare-a2a-agent-app.onrender.com",
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "authentication": {"type": "none"},
        "capabilities": {
            "streaming": False, 
            "pushNotifications": False, 
            "stateTransitionHistory": False
        },
        "skills": [
            {
                "id": "bp_analysis",
                "name": "BP Analysis",
                "description": "Classifies blood pressure",
                "tags": ["clinical"],
                "inputModes": ["application/json"],
                "outputModes": ["application/json"]
            }
        ],
        "supportedInterfaces": [
            {
                "type": "rest",
                "version": "1.0",
                "url": "https://healthcare-a2a-agent-app.onrender.com/task",
                "protocolBinding": "http",
                "protocolVersion": "1.0"
            }
        ],
        "api_endpoint": "https://healthcare-a2a-agent-app.onrender.com/task"
    }

@app.post("/task")
async def handle_task(payload: Dict[str, Any] = Body(...)):
    return {"status": "completed", "output": {"text": "Data received."}}

if __name__ == "__main__":
    # Render provides the PORT variable. Using 10000 as default.
    port = int(os.environ.get("PORT", 10000))
    # host MUST be 0.0.0.0 for external access
    uvicorn.run(app, host="0.0.0.0", port=port)
