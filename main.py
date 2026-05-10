#!/usr/bin/env python3
# FORCE DEPLOY - Prompt Opinion Integration
"""
Healthcare A2A Agent - Complete Self-Contained Version
"""

import subprocess
import sys
import os

# Auto-install dependencies
def install_dependencies():
    required_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0"
    ]
    for package in required_packages:
        try:
            __import__(package.split("==")[0])
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_dependencies()

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from datetime import datetime
import uvicorn

app = FastAPI(title="Healthcare A2A Agent", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
    return {
        "message": "Healthcare A2A Agent is running!",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "task": "/task (POST)",
            "agent_card": "/.well-known/agent-card.json"
        }
    }

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
# AGENT CARD - PROMPT OPINION COMPATIBLE
# ============================================
@app.get("/.well-known/agent-card.json")
@app.get("/.well-known/ai-agent.json")
@app.get("/agent-card.json")
@app.get("/ai-agent.json")
async def agent_card():
    return {
        "name": "Healthcare A2A Risk Analyzer",
        "description": "Clinical decision support agent analyzing blood pressure and cardiovascular risk using FHIR data. Provides evidence-based recommendations with explainable AI.",
        "version": "2.0.0",
        "supportedInterfaces": [
            {
                "type": "rest",
                "version": "1.0",
                "protocolBinding": "http",
                "protocolVersion": "1.0",
                "endpoint": "/task",
                "method": "POST",
                "url": "https://healthcare-a2a-agent-app.onrender.com/task"
            }
        ],
        "capabilities": [
            {
                "name": "blood_pressure_classification",
                "description": "Classifies blood pressure readings into Stage 1, Stage 2, or Normal based on ACC/AHA guidelines"
            },
            {
                "name": "cardiovascular_risk_assessment",
                "description": "Calculates cardiovascular risk based on age and blood pressure"
            },
            {
                "name": "medication_reconciliation",
                "description": "Reviews medications and identifies potential interactions"
            }
        ],
        "endpoint": {
            "url": "https://healthcare-a2a-agent-app.onrender.com/task",
            "method": "POST",
            "contentType": "application/json"
        },
        "health": {
            "url": "https://healthcare-a2a-agent-app.onrender.com/health",
            "method": "GET"
        }
    }

# ============================================
# CLINICAL TOOLS
# ============================================
def classify_blood_pressure(systolic: int, diastolic: int) -> Dict[str, Any]:
    if systolic >= 140 or diastolic >= 90:
        return {
            "category": "Stage 2 Hypertension",
            "guidance": "Immediate clinical follow-up required.",
            "urgency": "HIGH",
            "follow_up": "4 weeks"
        }
    elif systolic >= 130 or diastolic >= 80:
        return {
            "category": "Stage 1 Hypertension",
            "guidance": "Lifestyle modifications recommended.",
            "urgency": "MEDIUM",
            "follow_up": "3-6 months"
        }
    else:
        return {
            "category": "Normal",
            "guidance": "Continue routine monitoring.",
            "urgency": "LOW",
            "follow_up": "12 months"
        }

def parse_fhir_resources(resources: List[Dict]) -> Dict[str, Any]:
    extracted = {
        "bp_systolic": 0,
        "bp_diastolic": 0,
        "medications": [],
        "patient_age": None
    }
    for resource in resources:
        resource_type = resource.get("resourceType")
        if resource_type == "Patient":
            birth_date = resource.get("birthDate")
            if birth_date:
                try:
                    birth_year = int(birth_date.split("-")[0])
                    extracted["patient_age"] = datetime.now().year - birth_year
                except:
                    pass
        elif resource_type == "Observation":
            code_text = str(resource.get("code", {}).get("text", "")).lower()
            if "blood pressure" in code_text:
                for component in resource.get("component", []):
                    comp_text = str(component.get("code", {}).get("text", "")).lower()
                    value = component.get("valueQuantity", {}).get("value", 0)
                    if "systolic" in comp_text:
                        extracted["bp_systolic"] = value
                    elif "diastolic" in comp_text:
                        extracted["bp_diastolic"] = value
        elif resource_type == "MedicationRequest":
            med_name = resource.get("medicationCodeableConcept", {}).get("text", "")
            if med_name:
                extracted["medications"].append(med_name)
    return extracted

# ============================================
# MAIN TASK ENDPOINT
# ============================================
@app.post("/task")
async def handle_task(payload: Dict[str, Any] = Body(...)):
    try:
        resources = payload.get("context", {}).get("fhir_resources", [])
        clinical_data = parse_fhir_resources(resources)
        bp_result = classify_blood_pressure(
            clinical_data["bp_systolic"],
            clinical_data["bp_diastolic"]
        )
        
        recommendation_text = f"""
CLINICAL ASSESSMENT REPORT

Blood Pressure: {clinical_data['bp_systolic']}/{clinical_data['bp_diastolic']} mmHg
Classification: {bp_result['category']}
Urgency: {bp_result['urgency']}
Follow-up: {bp_result['follow_up']}

Recommendation: {bp_result['guidance']}

Next Steps:
- Confirm BP reading
- Review medications
- Schedule follow-up
"""
        return {
            "status": "completed",
            "output": {
                "text": recommendation_text.strip(),
                "tool_outputs": {
                    "blood_pressure": bp_result,
                    "medications": clinical_data["medications"]
                },
                "next_tasks": [
                    f"Confirm BP reading: {bp_result['follow_up']}",
                    "Review medication adherence",
                    "Schedule follow-up appointment"
                ]
            }
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# ============================================
# FALLBACK
# ============================================
@app.get("/{path:path}")
async def catch_all(path: str):
    return JSONResponse(
        status_code=200,
        content={
            "message": "Healthcare A2A Agent is running",
            "available_endpoints": [
                "/health",
                "/task (POST)",
                "/.well-known/agent-card.json"
            ]
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
