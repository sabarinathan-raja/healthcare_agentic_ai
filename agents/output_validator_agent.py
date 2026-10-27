
from typing import Any


def output_validator_agent(
    summary_result: dict[str, Any]
) -> dict[str, Any]:

    errors = []
    warnings = []

    # 1. Check input format
    if not isinstance(summary_result, dict):
        return {
            "status": "invalid_output",
            "is_valid": False,
            "errors": ["Input must be a dictionary."]
        }

    # 2. Check summary exists
    summary = summary_result.get("summary")

    if not isinstance(summary, dict):
        return {
            "status": "invalid_output",
            "is_valid": False,
            "errors": ["Summary is missing or invalid."]
        }

    # 3. Check required fields
    required_fields = [
        "patient_context",
        "missing_information",
        "evidence_summary",
        "evidence_status",
        "safety_status",
        "review_required",
        "review_reasons",
        "disclaimer",
    ]

    for field in required_fields:
        if field not in summary:
            errors.append(
                f"Required field is missing: {field}"
            )

    # 4. Check evidence source details
    evidence_items = summary.get("evidence_summary", [])

    if not isinstance(evidence_items, list):
        errors.append(
            "evidence_summary must be a list."
        )
    else:
        for index, evidence in enumerate(
            evidence_items, start=1
        ):
            if not isinstance(evidence, dict):
                errors.append(
                    f"Evidence item {index} is invalid."
                )
                continue

            if not evidence.get("source"):
                warnings.append(
                    f"Evidence item {index} has no source."
                )

            if evidence.get("page") is None:
                warnings.append(
                    f"Evidence item {index} has no page number."
                )

    # 5. Check safety review flag
    if "review_required" in summary:
        if not isinstance(summary["review_required"], bool):
            errors.append(
                "review_required must be True or False."
            )

    # 6. Check disclaimer
    if not summary.get("disclaimer"):
        warnings.append(
            "Clinical review disclaimer is missing."
        )

    # 7. Decide validation status
    is_valid = len(errors) == 0

    if not is_valid:
        status = "invalid_output"
    elif (
        summary.get("review_required") is True
        or warnings
    ):
        status = "review_required"
    else:
        status = "valid_output"

    return {
        "status": status,
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "human_review_required": (
            status != "valid_output"
        ),
    }


if __name__ == "__main__":

    # Synthetic test data only
    sample_summary = {
        "status": "summary_created",
        "summary": {
            "patient_context": {
                "age": 35,
                "documented_conditions": ["Asthma"],
            },
            "missing_information": [
                "current_medications",
                "allergies",
            ],
            "evidence_summary": [
                {
                    "source": (
                        "healthcare_demo_guideline_synthetic.pdf"
                    ),
                    "page": 1,
                    "text": (
                        "Synthetic text for testing only."
                    ),
                    "version": "1.0",
                    "publication_date": "2026-10-27",
                }
            ],
            "evidence_status": "review_required",
            "safety_status": "human_review_required",
            "review_required": True,
            "review_reasons": [
                "Patient information is incomplete."
            ],
            "disclaimer": (
                "Draft for qualified clinician review."
            ),
        },
    }

    result = output_validator_agent(sample_summary)

    print("\n===== OUTPUT VALIDATOR RESULT =====")
    print(result)
