
from typing import Any


def patient_context_agent(
    patient_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Extract documented patient facts and identify
    missing information.

    This agent does not diagnose or infer medical facts.
    """

    # Step 1: Validate the input
    if not isinstance(patient_data, dict):
        return {
            "status": "error",
            "message": "Patient data must be a dictionary."
        }

    # Step 2: Define the fields we want to check
    required_fields = [
        "age",
        "documented_conditions",
        "reported_symptoms",
        "current_medications",
        "allergies",
        "vital_signs"
    ]

    record_facts = {}
    missing_information = []

    # Step 3: Extract supplied facts
    for field in required_fields:
        value = patient_data.get(field)

        if value is None or value == "" or value == []:
            missing_information.append(field)
        else:
            record_facts[field] = value

    # Step 4: Return a structured result
    return {
        "status": "success",
        "record_facts": record_facts,
        "missing_information": missing_information,
        "message": (
            "Patient information extracted. "
            "Missing fields remain unknown and "
            "must not be inferred."
        )
    }


# Step 5: Test the agent
if __name__ == "__main__":

    sample_patient = {
        "age": 35,
        "documented_conditions": ["Asthma"],
        "reported_symptoms": ["Worsening cough"],
        "current_medications": None,
        "allergies": None,
        "vital_signs": None
    }

    result = patient_context_agent(sample_patient)

    print("\n===== PATIENT CONTEXT AGENT =====")
    print("\nDocumented Patient Facts:")

    for key, value in result.get(
        "record_facts", {}
    ).items():
        print(f"{key}: {value}")

    print("\nMissing Information:")

    for field in result.get(
        "missing_information", []
    ):
        print(f"- {field}")

    print("\nStatus:", result["status"])
