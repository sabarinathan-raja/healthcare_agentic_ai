
import pytest

from agents.intake_agent import intake_agent
from agents.patient_context_agent import patient_context_agent
from agents.evidence_quality_agent import evidence_quality_agent
from agents.safety_agent import safety_agent
from agents.summary_agent import summary_agent
from agents.output_validator_agent import output_validator_agent


# ==========================================
# TEST 1: INTAKE AGENT
# ==========================================

def test_intake_accepts_evidence_search():
    result = intake_agent(
        "Find the section that mentions asthma in the demonstration document."
    )

    assert isinstance(result, dict)
    assert result.get("scope_status") == "accepted_for_processing"


def test_intake_handles_empty_request():
    result = intake_agent("")

    assert isinstance(result, dict)

    # An empty request must not be accepted for processing.
    assert result.get("scope_status") != "accepted_for_processing"


def test_intake_flags_medication_request():
    result = intake_agent("Prescribe medication for me.")

    assert isinstance(result, dict)

    # Medication decisions should not be processed as
    # ordinary evidence-search requests.
    assert result.get("scope_status") != "accepted_for_processing"


# ==========================================
# TEST 2: PATIENT CONTEXT AGENT
# ==========================================

def test_patient_context_detects_missing_information():
    patient_data = {
        "age": 35,
        "documented_conditions": ["Asthma"],
        "reported_symptoms": ["Worsening cough"],
        "current_medications": None,
        "allergies": None,
        "vital_signs": None,
    }

    result = patient_context_agent(patient_data)

    assert isinstance(result, dict)
    assert "record_facts" in result
    assert "missing_information" in result

    missing = result["missing_information"]

    assert "current_medications" in missing
    assert "allergies" in missing
    assert "vital_signs" in missing


# ==========================================
# TEST 3: EVIDENCE QUALITY AGENT
# ==========================================

def test_evidence_quality_flags_missing_metadata():
    question = "Find the section about asthma."

    documents = [
        {
            "text": "This section mentions asthma for a retrieval test.",
            "source": "demo.pdf",
            "page": 1,
            "version": None,
            "publication_date": None,
        }
    ]

    result = evidence_quality_agent(
        question,
        documents,
    )

    assert isinstance(result, dict)
    assert result["review_required"] is True
    assert result["status"] == "review_required"
    assert len(result["review_reasons"]) > 0


def test_evidence_quality_accepts_basic_complete_metadata():
    question = "Find the section about asthma."

    documents = [
        {
            "text": (
                "This section mentions asthma. "
                "It is a synthetic document for testing."
            ),
            "source": "demo.pdf",
            "page": 1,
            "version": "1.0",
            "publication_date": "2026-10-27",
        }
    ]

    result = evidence_quality_agent(
        question,
        documents,
    )

    assert result["status"] == "basic_checks_passed"
    assert result["review_required"] is False


# ==========================================
# TEST 4: SAFETY AGENT
# ==========================================

def test_safety_agent_requires_review_for_missing_data():
    patient_context = {
        "status": "success",
        "record_facts": {
            "age": 35,
            "documented_conditions": ["Asthma"],
        },
        "missing_information": [
            "current_medications",
            "allergies",
            "vital_signs",
        ],
    }

    evidence_result = {
        "status": "basic_checks_passed",
        "evidence": [],
        "review_required": False,
        "review_reasons": [],
    }

    result = safety_agent(
        patient_context,
        evidence_result,
        "Find the section about asthma.",
    )

    assert result["review_required"] is True
    assert "missing_patient_information" in result["safety_flags"]


# ==========================================
# TEST 5: SUMMARY AGENT
# ==========================================

def test_summary_contains_required_information():
    patient_context = {
        "status": "success",
        "record_facts": {
            "age": 35,
            "documented_conditions": ["Asthma"],
        },
        "missing_information": ["allergies"],
    }

    evidence_result = {
        "status": "review_required",
        "evidence": [
            {
                "source": "demo.pdf",
                "page": 1,
                "text": "Synthetic asthma retrieval test.",
                "version": "1.0",
                "publication_date": "2026-10-27",
            }
        ],
        "review_required": True,
        "review_reasons": ["Manual review required."],
    }

    safety_result = {
        "status": "human_review_required",
        "review_required": True,
        "review_reasons": ["Allergy information is missing."],
    }

    result = summary_agent(
        patient_context,
        evidence_result,
        safety_result,
    )

    assert result["status"] == "summary_created"

    summary = result["summary"]

    assert "patient_context" in summary
    assert "missing_information" in summary
    assert "evidence_summary" in summary
    assert "review_required" in summary
    assert summary["review_required"] is True
    assert summary["disclaimer"]


# ==========================================
# TEST 6: OUTPUT VALIDATOR
# ==========================================

def test_validator_accepts_structure_but_requires_review():
    summary_result = {
        "status": "summary_created",
        "summary": {
            "patient_context": {"age": 35},
            "missing_information": ["allergies"],
            "evidence_summary": [
                {
                    "source": "demo.pdf",
                    "page": 1,
                    "text": "Synthetic testing text.",
                    "version": "1.0",
                    "publication_date": "2026-10-27",
                }
            ],
            "evidence_status": "review_required",
            "safety_status": "human_review_required",
            "review_required": True,
            "review_reasons": ["Manual review required."],
            "disclaimer": "Draft for clinician review.",
        },
    }

    result = output_validator_agent(summary_result)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["human_review_required"] is True


def test_validator_rejects_invalid_summary():
    result = output_validator_agent({
        "status": "summary_created",
        "summary": {},
    })

    assert result["is_valid"] is False
    assert result["status"] == "invalid_output"
    assert len(result["errors"]) > 0
