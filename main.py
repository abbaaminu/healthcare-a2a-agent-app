import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from datetime import datetime
import uvicorn

app = FastAPI(title="Healthcare A2A Agent", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "ready": True}

@app.get("/ai-agent.json")
@app.get("/.well-known/ai-agent.json")
async def agent_card():
    return {
        "name": "Healthcare A2A Risk Analyzer",
        "description": "Clinical decision support agent analyzing BP and cardiovascular risk",
        "version": "2.0.0",
        "url": "https://healthcare-a2a-agent-app.onrender.com",
        "capabilities": ["clinical_analysis", "medication_reconciliation"],
        # Add this: Dashboards often crash if authentication is missing
        "authentication": {
            "type": "none"
        },
        "supportedInterfaces": [
            {
                "type": "rest",
                "version": "1.0",
                "url": "https://healthcare-a2a-agent-app.onrender.com/task",
                "protocolBinding": "http"
            }
        ],
        "api_endpoint": "https://healthcare-a2a-agent-app.onrender.com/task"
    }

@app.get("/")
async def root():
    return {"message": "Healthcare A2A Agent is running"}

@app.post("/task")
async def handle_task(payload: Dict[str, Any] = Body(...)):
    try:
        context = payload.get("context", {})
        resources = context.get("fhir_resources", [])
        
        systolic = 0
        diastolic = 0
        medications = []
        
        for resource in resources:
            if resource.get("resourceType") == "Observation":
                text = resource.get("code", {}).get("text", "")
                if "Blood Pressure" in text:
                    for comp in resource.get("component", []):
                        val = comp.get("valueQuantity", {}).get("value", 0)
                        c_text = comp.get("code", {}).get("text", "")
                        if "Systolic" in c_text:
                            systolic = val
                        elif "Diastolic" in c_text:
                            diastolic = val
            elif resource.get("resourceType") == "MedicationRequest":
                med = resource.get("medicationCodeableConcept", {}).get("text", "")
                if med:
                    medications.append(med)
        
        if systolic >= 140 or diastolic >= 90:
            cat = "Stage 2 Hypertension"
        elif systolic >= 130 or diastolic >= 80:
            cat = "Stage 1 Hypertension"
        else:
            cat = "Normal"
            
        return {
            "status": "completed",
            "output": {
                "text": f"Result: {systolic}/{diastolic} - {cat}",
                "tool_outputs": {"category": cat, "meds": medications}
            }
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
