#!/usr/bin/env python3
# FORCE DEPLOY - Prompt Opinion Integration
"""
Healthcare A2A Agent - Complete Self-Contained Version
Prompt Opinion Compatible - Fixed Agent Card Format
"""

import subprocess
import sys
import os

# Auto-install dependencies when script runs
def install_dependencies():
    """Install required packages automatically"""
    required_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0"
    ]
    
    for package in required_packages:
        try:
            __import__(package.split("==")[0])
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

# Install dependencies before importing
install_dependencies()

# Now import everything
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(title="Healthcare A2A Agent", version="2.0.0")

# ============================================
# CORS MIDDLEWARE (Required for Prompt Opinion)
# ============================================
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
        "message": "🏥 Healthcare A2A Agent is running!",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "task": "/task (POST)",
            "agent_card": "/.well-known/ai-agent.json"
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
# AGENT CARD - COMPLETE PROMPT OPINION FORMAT
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
    {"name": "blood_pressure_classification"},
    {"name": "cardiovascular_risk_assessment"},
    {"name": "medication_reconciliation"}
]
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
    """Blood Pressure Classification based on ACC/AHA 2017 Guidelines"""
    if systolic >= 140 or diastolic >= 90:
        return {
            "category": "Stage 2 Hypertension",
            "guidance": "Immediate clinical follow-up required. Consider initiating or adjusting antihypertensive medication. Target BP <130/80.",
            "urgency": "HIGH",
            "follow_up": "4 weeks or sooner",
            "recommendations": [
                "Start or titrate antihypertensive medication",
                "Consider dual therapy if BP >150/90",
                "Evaluate for target organ damage",
                "Lifestyle modifications"
            ]
        }
    elif systolic >= 130 or diastolic >= 80:
        return {
            "category": "Stage 1 Hypertension",
            "guidance": "Lifestyle modifications recommended. If 10-year ASCVD risk >10%, consider pharmacotherapy.",
            "urgency": "MEDIUM",
            "follow_up": "3-6 months",
            "recommendations": [
                "DASH diet (fruits, vegetables, low-fat dairy)",
                "Reduce sodium to <1500mg/day",
                "Increase physical activity to 150 min/week",
                "Limit alcohol",
                "Consider pharmacotherapy if high risk"
            ]
        }
    else:
        return {
            "category": "Normal",
            "guidance": "Continue routine monitoring annually. Maintain healthy lifestyle.",
            "urgency": "LOW",
            "follow_up": "12 months",
            "recommendations": [
                "Annual BP screening",
                "Maintain healthy weight",
                "Regular exercise",
                "Balanced diet"
            ]
        }

def calculate_cardiovascular_risk(age: int, bp_category: str) -> Dict[str, Any]:
    """Simplified cardiovascular risk assessment"""
    risk_score = 0
    
    if age > 75:
        risk_score += 3
    elif age > 65:
        risk_score += 2
    elif age > 55:
        risk_score += 1
    
    if bp_category == "Stage 2 Hypertension":
        risk_score += 2
    elif bp_category == "Stage 1 Hypertension":
        risk_score += 1
    
    if risk_score >= 4:
        risk_level = "HIGH"
        recommendation = "High cardiovascular risk. Aggressive risk factor modification needed."
    elif risk_score >= 2:
        risk_level = "MODERATE"
        recommendation = "Moderate cardiovascular risk. Lifestyle modifications and risk factor control."
    else:
        risk_level = "LOW"
        recommendation = "Low cardiovascular risk. Continue preventive health measures."
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendation": recommendation
    }

def parse_fhir_resources(resources: List[Dict]) -> Dict[str, Any]:
    """Extract clinical data from FHIR resources"""
    extracted = {
        "bp_systolic": 0,
        "bp_diastolic": 0,
        "medications": [],
        "patient_age": None,
        "patient_gender": None,
        "conditions": []
    }
    
    for resource in resources:
        resource_type = resource.get("resourceType")
        
        if resource_type == "Patient":
            extracted["patient_gender"] = resource.get("gender")
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
                components = resource.get("component", [])
                for component in components:
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
        
        elif resource_type == "Condition":
            condition_name = resource.get("code", {}).get("text", "")
            if condition_name:
                extracted["conditions"].append(condition_name)
    
    return extracted

# ============================================
# MAIN TASK ENDPOINT
# ============================================
@app.post("/task")
async def handle_task(payload: Dict[str, Any] = Body(...)):
    """Main clinical analysis endpoint"""
    try:
        resources = payload.get("context", {}).get("fhir_resources", [])
        
        # Parse FHIR resources
        clinical_data = parse_fhir_resources(resources)
        
        # Classify blood pressure
        bp_result = classify_blood_pressure(
            clinical_data["bp_systolic"],
            clinical_data["bp_diastolic"]
        )
        
        # Calculate cardiovascular risk if age available
        cv_risk = None
        if clinical_data["patient_age"]:
            cv_risk = calculate_cardiovascular_risk(
                clinical_data["patient_age"],
                bp_result["category"]
            )
        
        # Build reasoning trace
        reasoning_trace = [
            f"Parsed {len(resources)} FHIR resources",
            f"BP: {clinical_data['bp_systolic']}/{clinical_data['bp_diastolic']} mmHg",
            f"BP Classification: {bp_result['category']}",
            f"Found {len(clinical_data['medications'])} medications"
        ]
        
        # Build clinical recommendation text
        recommendation_text = f"""
🏥 CLINICAL ASSESSMENT REPORT

📊 VITAL SIGNS
• Blood Pressure: {clinical_data['bp_systolic']}/{clinical_data['bp_diastolic']} mmHg
• Classification: {bp_result['category']}
• Urgency: {bp_result['urgency']}
• Follow-up: {bp_result['follow_up']}

📋 RECOMMENDATION
{bp_result['guidance']}

✅ NEXT STEPS
"""
        for rec in bp_result['recommendations']:
            recommendation_text += f"\n• {rec}"
        
        # Build final response
        return {
            "status": "completed",
            "output": {
                "text": recommendation_text.strip(),
                "tool_outputs": {
                    "blood_pressure": {
                        "systolic": clinical_data["bp_systolic"],
                        "diastolic": clinical_data["bp_diastolic"],
                        "category": bp_result["category"],
                        "guidance": bp_result["guidance"],
                        "urgency": bp_result["urgency"]
                    },
                    "medications": clinical_data["medications"],
                    "patient_age": clinical_data["patient_age"]
                },
                "next_tasks": [
                    f"Confirm BP reading: {bp_result['follow_up']}",
                    "Review medication adherence",
                    "Schedule follow-up appointment"
                ],
                "reasoning_trace": reasoning_trace
            }
        }
    
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🏥 Healthcare A2A Agent starting on port {port}...")
    print(f"📋 Health check: http://localhost:{port}/health")
    print(f"🤖 Agent card: http://localhost:{port}/.well-known/ai-agent.json")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=port)
