import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Agent is Online"}

@app.get("/.well-known/agent-card.json")
@app.get("/ai-agent.json")
async def agent_card():
    return {
        "name": "Healthcare Risk Agent",
        "description": "Analyzing cardiovascular risk factors.",
        "version": "1.0.0",
        "url": "https://healthcare-a2a-agent-app.onrender.com",
        "authentication": {"type": "none"},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "capabilities": {
            "streaming": False,
            "pushNotifications": False
        },
        "skills": [
            {
                "id": "risk-check",
                "name": "Health Risk Check",
                "description": "Checks health data",
                "tags": ["health"],
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
                "protocolVersion": "1.1"
            }
        ]
    }

@app.post("/task")
async def task():
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
