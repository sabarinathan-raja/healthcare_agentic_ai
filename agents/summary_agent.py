
from typing import Any


def summary_agent(
    patient_context: dict[str, Any],
    evidence_result: dict[str, Any],
    safety_result: dict[str, Any],
) -> dict[str, Any]:

    # Validate inputs
    if not isinstance(patient_context, dict):
        return {
            "status": "error",
            "message": "Invalid patient context."
        }

    if not isinstance(evidence_result, dict):
        return {
            "status": "error",
            "message": "Invalid evidence result."
        }

    if not isinstance(safety_result, dict):
        return {
            "status": "error",
            "message": "Invalid safety result."
        }

    # Collect patient information
    patient_facts = patient_context.get(
        "record_facts", {}
    )

    missing_information = patient_context.get(
        "missing_information", []
    )

    # Collect retrieved evidence
    evidence_items = evidence_result.get(
        "evidence", []
    )

    evidence_summary = []

    for item in evidence_items:
        evidence_summary.append({
            "source": item.get("source"),
            "page": item.get("page"),
            "text": item.get("text", ""),
            "version": item.get("version"),
            "publication_date": item.get(
                "publication_date"
            ),
        })

    # Check whether human review is required
    review_required = (
        patient_context.get("status") == "error"
        or evidence_result.get("review_required", True)
        or safety_result.get("review_required", True)
    )

    # Create structured summary
    summary = {
        "patient_context": patient_facts,
        "missing_information": missing_information,
        "evidence_summary": evidence_summary,
        "evidence_status": evidence_result.get(
            "status", "unknown"
        ),
        "safety_status": safety_result.get(
            "status", "unknown"
        ),
        "review_required": review_required,
        "review_reasons": (
            evidence_result.get("review_reasons", [])
            + safety_result.get("review_reasons", [])
        ),
        "disclaimer": (
            "This is a draft for qualified clinician review. "
            "It is not a diagnosis or treatment recommendation."
        ),
    }

    return {
        "status": "summary_created",
        "summary": summary,
    }


if __name__ == "__main__":

    # Synthetic test data only
    patient_context = {
        "status": "context_extracted",
        "record_facts": {
            "age": 35,
            "documented_conditions": ["Asthma"],
            "reported_symptoms": ["Worsening cough"],
        },
        "missing_information": [
            "current_medications",
            "allergies",
            "vital_signs",
        ],
    }

    evidence_result = {
        "status": "review_required",
        "evidence": [
            {
                "source": "healthcare_demo_guideline_synthetic.pdf",
                "page": 1,
                "text": (
                    "Synthetic demonstration text for "
                    "testing evidence retrieval."
                ),
                "version": "1.0",
                "publication_date": "2026-10-27",
            }
        ],
        "review_required": True,
        "review_reasons": [
            "Evidence needs manual review."
        ],
    }

    safety_result = {
        "status": "human_review_required",
        "review_required": True,
        "review_reasons": [
            "Some patient information is missing."
        ],
    }

    result = summary_agent(
        patient_context,
        evidence_result,
        safety_result,
    )

    print("\n===== SUMMARY AGENT OUTPUT =====")
    print(result)
