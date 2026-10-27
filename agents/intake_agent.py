
from typing import Any


def intake_agent(user_request: str) -> dict[str, Any]:
    """
    Understand and validate the incoming healthcare request.
    This agent does not diagnose or prescribe medication.
    """

    # Step 1: Check whether input is empty
    if not isinstance(user_request, str) or not user_request.strip():
        return {
            "request": "",
            "request_type": "invalid",
            "scope_status": "rejected",
            "message": "Please provide a valid request."
        }

    request = user_request.strip()
    normalized_request = request.lower()

    # Step 2: Identify requests requiring clinical decisions
    clinical_decision_terms = [
        "diagnose me",
        "give me a diagnosis",
        "prescribe medication",
        "change my medication",
        "which medicine should i take",
        "what medicine should i take"
    ]

    if any(term in normalized_request
           for term in clinical_decision_terms):
        return {
            "request": request,
            "request_type": "clinical_decision",
            "scope_status": "human_review_required",
            "message": (
                "This system cannot provide a diagnosis "
                "or recommend medication changes. "
                "Please consult a qualified healthcare professional."
            )
        }

    # Step 3: Check whether the request is related
    # to the healthcare evidence-summary project
    healthcare_terms = [
        "patient",
        "medical",
        "healthcare",
        "clinical",
        "asthma",
        "evidence",
        "symptom",
        "guideline"
    ]

    if not any(term in normalized_request
               for term in healthcare_terms):
        return {
            "request": request,
            "request_type": "out_of_scope",
            "scope_status": "rejected",
            "message": (
                "Please provide a healthcare-related "
                "evidence-summary request."
            )
        }

    # Step 4: Accept the request for further processing
    return {
        "request": request,
        "request_type": "evidence_summary",
        "scope_status": "accepted_for_processing",
        "message": (
            "Request accepted for further processing. "
            "Clinical facts and evidence must be validated "
            "by subsequent workflow stages."
        )
    }


# Step 5: Run a sample request
if __name__ == "__main__":

    sample_request = (
        "Prepare an evidence summary for a patient "
        "with a documented history of asthma."
    )

    result = intake_agent(sample_request)

    print("\n===== INTAKE AGENT RESULT =====")

    for key, value in result.items():
        print(f"{key}: {value}")
