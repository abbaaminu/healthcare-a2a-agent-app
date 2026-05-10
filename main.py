import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# THIS IS THE KEY: It tells the browser/dashboard that it's safe to read your data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "TechWithAb Healthcare Agent is Live"}

@app.get("/.well-known/agent-card.json")
@app.get("/ai-agent.json")
async def agent_card():
    return {
        "name": "Healthcare Risk Agent",
        "description": "Clinical decision support for BP and Cardiovascular risk",
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
                "protocolVersion": "1.1"
            }
        ]
    }

@app.post("/task")
async def task_handler():
    return {"status": "success", "message": "Task processed"}

if __name__ == "__main__":
    # Use Render's PORT or default to 10000
    port = int(os.environ.get("PORT", 10000))
    # Passing the app as a string "main:app" is the most stable way on Render
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
