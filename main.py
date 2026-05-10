#!/usr/bin/env python3
# FORCE DEPLOY - Prompt Opinion Integration
"""
Healthcare A2A Agent - Working Version for Render
"""

import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(title="Healthcare A2A Agent", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Healthcare A2A Agent",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "ready": True
    }

# ============================================
# AGENT CARD - A2A COMPLIANT
# ============================================
@app.get("/.well-known/agent-card.json")
@app.get("/.well-known/ai-agent.json")
@app.get("/agent-card.json")
async def agent_card():
    return {
        "name": "Healthcare A2A Risk Analyzer",
        "description": "Clinical decision support agent analyzing blood pressure and cardiovascular risk",
        "version": "2.0.0",
        "url": "https://healthcare-a2a-agent-app.onrender.com",
        
        "authentication": {
            "schemes": []
        },
        
        # FIX: Capabilities must be a LIST of IDs
        "capabilities": [
            "clinical_analysis",
            "medication_reconciliation"
        ],
        
        "skills": [
            {
                "id": "blood_pressure_classification",
                "name": "Blood Pressure Classification",
                "description": "Classifies blood pressure readings into Stage 1, Stage 2, or Normal",
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
        ]
    }
        
        # === ENDPOINTS ===
        "endpoint": "https://healthcare-a2a-agent-app.onrender.com/task",
        "health": "https://healthcare-a2a-agent-app.onrender.com/health"
    }
# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
    return {
        "message": "Healthcare A2A Agent is running",
        "version": "2.0.0",
        "endpoints": ["/health", "/task (POST)", "/.well-known/agent-card.json"]
    }

# ============================================
# MAIN TASK ENDPOINT
# ============================================
@app.post("/task")
async def handle_task(payload: Dict[str, Any] = Body(...)):
    try:
        resources = payload.get("context", {}).get("fhir_resources", [])
        
        # Extract BP
        systolic = 0
        diastolic = 0
        medications = []
        
        for resource in resources:
            if resource.get("resourceType") == "Observation":
                code = str(resource.get("code", {}).get("text", ""))
                if "Blood Pressure" in code:
                    for comp in resource.get("component", []):
                        val = comp.get("valueQuantity", {}).get("value", 0)
                        comp_code = str(comp.get("code", {}).get("text", ""))
                        if "Systolic" in comp_code:
                            systolic = val
                        elif "Diastolic" in comp_code:
                            diastolic = val
            elif resource.get("resourceType") == "MedicationRequest":
                med_name = resource.get("medicationCodeableConcept", {}).get("text", "")
                if med_name:
                    medications.append(med_name)
        
        # Classify BP
        if systolic >= 140 or diastolic >= 90:
            category = "Stage 2 Hypertension"
            rec = "Immediate clinical follow-up required"
        elif systolic >= 130 or diastolic >= 80:
            category = "Stage 1 Hypertension"
            rec = "Lifestyle modifications recommended"
        else:
            category = "Normal"
            rec = "Continue routine monitoring"
        
        return {
            "status": "completed",
            "output": {
                "text": f"BP: {systolic}/{diastolic} - {category}. {rec}",
                "tool_outputs": {
                    "blood_pressure": {
                        "systolic": systolic,
                        "diastolic": diastolic,
                        "category": category
                    },
                    "medications": medications
                },
                "next_tasks": [
                    "Confirm BP reading in clinic",
                    "Review medication adherence",
                    "Schedule follow-up appointment"
                ]
            }
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

# ============================================
# FALLBACK HANDLER
# ============================================
@app.get("/{path:path}")
async def catch_all(path: str):
    return JSONResponse(
        status_code=200,
        content={
            "message": "Healthcare A2A Agent is running",
            "available_endpoints": [
                "/",
                "/health",
                "/task (POST)",
                "/.well-known/agent-card.json"
            ]
        }
    )

# ============================================
# RUN THE APP
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
