
from typing import Any

from agents.intake_agent import intake_agent
from agents.patient_context_agent import patient_context_agent
from agents.evidence_quality_agent import evidence_quality_agent
from agents.safety_agent import safety_agent
from agents.summary_agent import summary_agent
from agents.output_validator_agent import output_validator_agent

from retrieval.document_loader import (
    load_medical_pdfs,
    split_documents,
    create_vector_database,
    retrieve_evidence,
)


def run_healthcare_workflow(
    user_request: str,
    patient_data: dict[str, Any],
) -> dict[str, Any]:

    print("\n=== STEP 1: INTAKE AGENT ===")

    intake_result = intake_agent(user_request)
    print(intake_result)

    # Stop if request is not accepted
    if not isinstance(intake_result, dict):
        return {
            "status": "stopped",
            "reason": "Invalid intake output.",
        }

    intake_status = str(
        intake_result.get("status", "")
    ).lower()

    if (
        intake_status in {
            "error",
            "out_of_scope",
            "human_review_required",
        }
        or intake_result.get("review_required") is True
    ):
        return {
            "status": "stopped_at_intake",
            "intake_result": intake_result,
            "message": (
                "Request needs correction or human review."
            ),
        }

    print("\n=== STEP 2: PATIENT CONTEXT AGENT ===")

    context_result = patient_context_agent(patient_data)
    print(context_result)

    print("\n=== STEP 3: DOCUMENT RETRIEVAL ===")

    documents = load_medical_pdfs()
    chunks = split_documents(documents)

    if not chunks:
        return {
            "status": "stopped_at_retrieval",
            "message": "No readable document chunks found.",
        }

    vector_db = create_vector_database(chunks)

    retrieved = retrieve_evidence(
        vector_db,
        user_request,
        k=3,
    )

    # Convert retrieved LangChain documents
    # into dictionaries for the quality agent.
    retrieved_documents = []

    for document, distance_score in retrieved:
        metadata = document.metadata
        page_index = metadata.get("page")

        retrieved_documents.append({
            "text": document.page_content,
            "source": metadata.get("source"),
            "page": (
                page_index + 1
                if isinstance(page_index, int)
                else page_index
            ),
            "version": metadata.get("version"),
            "publication_date": metadata.get(
                "publication_date"
            ),
            "distance_score": float(distance_score),
        })

    print(f"Retrieved documents: {len(retrieved_documents)}")

    print("\n=== STEP 4: EVIDENCE QUALITY AGENT ===")

    evidence_result = evidence_quality_agent(
        user_request,
        retrieved_documents,
    )
    print(evidence_result)

    print("\n=== STEP 5: SAFETY AGENT ===")

    safety_result = safety_agent(
        context_result,
        evidence_result,
        user_request,
    )
    print(safety_result)

    print("\n=== STEP 6: SUMMARY AGENT ===")

    summary_result = summary_agent(
        context_result,
        evidence_result,
        safety_result,
    )
    print(summary_result)

    print("\n=== STEP 7: OUTPUT VALIDATOR ===")

    validation_result = output_validator_agent(
        summary_result
    )
    print(validation_result)

    # Do not describe the output as clinically validated.
    return {
        "status": "workflow_completed",
        "intake": intake_result,
        "patient_context": context_result,
        "evidence": evidence_result,
        "safety": safety_result,
        "summary": summary_result,
        "validation": validation_result,
        "clinical_review_required": True,
    }


if __name__ == "__main__":

    # Synthetic example data for development only
    request = input(
        "Enter a healthcare evidence search question: "
    ).strip()

    patient_data = {
        "age": 35,
        "documented_conditions": ["Asthma"],
        "reported_symptoms": ["Worsening cough"],
        "current_medications": None,
        "allergies": None,
        "vital_signs": None,
    }

    if not request:
        print("Please enter a question.")
    else:
        try:
            result = run_healthcare_workflow(
                request,
                patient_data,
            )

            print("\n=== FINAL WORKFLOW RESULT ===")
            print(result)

        except Exception as error:
            print("\nWorkflow failed.")
            print(f"Error: {error}")
            print(
                "Check imports, package installation, "
                "and PDF availability."
            )
