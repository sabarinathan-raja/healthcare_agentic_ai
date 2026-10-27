
from typing import Any


def safety_agent(
    patient_context: dict[str, Any],
    evidence_result: dict[str, Any],
    user_request: str = ""
) -> dict[str, Any]:
    """
    Perform basic safety checks for the healthcare workflow.

    This is a prototype, not a clinical safety system.
    """

    safety_flags = []
    review_reasons = []

    # Step 1: Validate input structures
    if not isinstance(patient_context, dict):
        return {
            "status": "error",
            "review_required": True,
            "safety_flags": ["invalid_patient_context"],
            "review_reasons": [
                "Patient context must be a dictionary."
            ]
        }

    if not isinstance(evidence_result, dict):
        return {
            "status": "error",
            "review_required": True,
            "safety_flags": ["invalid_evidence_result"],
            "review_reasons": [
                "Evidence result must be a dictionary."
            ]
        }

    # Step 2: Check missing patient information
    missing_information = patient_context.get(
        "missing_information", []
    )

    if missing_information:
        safety_flags.append("missing_patient_information")
        review_reasons.append(
            "Patient information is missing: "
            + ", ".join(map(str, missing_information))
        )

    # Step 3: Check evidence quality result
    if evidence_result.get("review_required", True):
        safety_flags.append("evidence_review_required")
        review_reasons.append(
            "Retrieved evidence needs further review."
        )

    if evidence_result.get("status") in {
        "error",
        "no_usable_evidence"
    }:
        safety_flags.append("evidence_unavailable")
        review_reasons.append(
            "Usable evidence was not available."
        )

    # Step 4: Check for requests outside the intended scope
    request = user_request.lower()

    clinical_decision_terms = [
        "diagnose me",
        "give me a diagnosis",
        "prescribe medication",
        "change my medication",
        "which medicine should i take",
        "what medicine should i take"
    ]

    if any(term in request for term in clinical_decision_terms):
        safety_flags.append("clinical_decision_request")
        review_reasons.append(
            "Diagnosis and medication decisions require "
            "a qualified healthcare professional."
        )

    # Step 5: Determine whether human review is needed
    review_required = bool(safety_flags)

    if review_required:
        status = "human_review_required"
    else:
        status = "basic_safety_checks_passed"

    # Step 6: Return safety assessment
    return {
        "status": status,
        "review_required": review_required,
        "safety_flags": safety_flags,
        "review_reasons": review_reasons,
        "limitations": [
            "This prototype does not diagnose or prescribe.",
            "Keyword checks cannot detect every unsafe request.",
            "Human review may be required before clinical use."
        ]
    }


if __name__ == "__main__":

    # Synthetic test data only
    sample_patient_context = {
        "status": "success",
        "record_facts": {
            "documented_conditions": ["Asthma"],
            "reported_symptoms": ["Worsening cough"]
        },
        "missing_information": [
            "current_medications",
            "vital_signs"
        ]
    }

    sample_evidence_result = {
        "status": "review_required",
        "review_required": True,
        "evidence": [],
        "review_reasons": [
            "Evidence needs further review."
        ]
    }

    result = safety_agent(
        patient_context=sample_patient_context,
        evidence_result=sample_evidence_result,
        user_request=(
            "Prepare an evidence summary for a patient "
            "with asthma."
        )
    )

    print("\n===== SAFETY AGENT RESULT =====")
    print("Status:", result["status"])
    print("Review required:", result["review_required"])

    print("\nSafety flags:")
    for flag in result["safety_flags"]:
        print("-", flag)

    print("\nReview reasons:")
    for reason in result["review_reasons"]:
        print("-", reason)
