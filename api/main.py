
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from orchestration.orchestrator import run_healthcare_workflow


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Healthcare Agentic AI API",
    description=(
        "A prototype multi-agent workflow for "
        "healthcare evidence retrieval and review."
    ),
    version="1.0.0",
)


# ==========================================
# REQUEST MODEL
# ==========================================

class HealthcareRequest(BaseModel):
    user_request: str = Field(
        ...,
        min_length=1,
        description="Question to search in the supplied documents.",
    )

    patient_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Patient context for prototype testing.",
    )


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Healthcare Agentic AI API is running.",
        "docs": "/docs",
        "health_check": "/health",
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Healthcare Agentic AI",
    }


# ==========================================
# RUN HEALTHCARE WORKFLOW
# ==========================================

@app.post("/run")
def run_workflow(request: HealthcareRequest):

    user_request = request.user_request.strip()

    if not user_request:
        raise HTTPException(
            status_code=422,
            detail="Please provide a non-empty search question.",
        )

    try:
        result = run_healthcare_workflow(
            user_request=user_request,
            patient_data=request.patient_data,
        )

        return {
            "api_status": "success",
            "workflow_result": result,
            "clinical_review_required": True,
            "notice": (
                "Prototype only. Results are not a diagnosis "
                "or treatment recommendation. Qualified "
                "clinical review is required."
            ),
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=(
                "Required PDF documents were not found. "
                "Check sources/medical_documents."
            ),
        )

    except Exception as error:
        # Keep technical details in the server terminal,
        # not in the API response.
        print(f"Workflow error: {type(error).__name__}: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "The healthcare workflow failed. "
                "Check the backend terminal for details."
            ),
        )
