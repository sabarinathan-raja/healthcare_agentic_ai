
from typing import Any


def evidence_quality_agent(
    question: str,
    retrieved_documents: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Perform basic quality checks on retrieved evidence.

    This is a rule-based prototype, not a clinical
    evidence validation system.
    """

    # Step 1: Validate the input
    if not isinstance(question, str) or not question.strip():
        return {
            "status": "error",
            "evidence": [],
            "review_required": True,
            "message": "A valid question is required."
        }

    if not isinstance(retrieved_documents, list):
        return {
            "status": "error",
            "evidence": [],
            "review_required": True,
            "message": "Retrieved documents must be a list."
        }

    question_words = {
        word.lower().strip(".,?!:;")
        for word in question.split()
        if len(word) > 2
    }

    verified_evidence = []
    review_reasons = []

    # Step 2: Inspect each retrieved document
    for index, document in enumerate(retrieved_documents, start=1):

        if not isinstance(document, dict):
            review_reasons.append(
                f"Result {index}: invalid document format."
            )
            continue

        text = document.get("text", "")
        source = document.get("source")
        page = document.get("page")
        version = document.get("version")
        publication_date = document.get("publication_date")

        if not isinstance(text, str) or not text.strip():
            review_reasons.append(
                f"Result {index}: empty document text."
            )
            continue

        # Step 3: Check basic source metadata
        missing_metadata = []

        if not source:
            missing_metadata.append("source")

        if page is None:
            missing_metadata.append("page")

        if missing_metadata:
            review_reasons.append(
                f"Result {index}: missing metadata: "
                + ", ".join(missing_metadata)
            )

        # Step 4: Basic keyword relevance check
        text_words = {
            word.lower().strip(".,?!:;")
            for word in text.split()
        }

        matched_words = question_words.intersection(text_words)

        relevance_ratio = (
            len(matched_words) / len(question_words)
            if question_words else 0.0
        )

        evidence_item = {
            "result_number": index,
            "text": text,
            "source": source,
            "page": page,
            "version": version,
            "publication_date": publication_date,
            "matched_keywords": sorted(matched_words),
            "keyword_relevance_ratio": round(
                relevance_ratio, 2
            ),
            "metadata_complete": not missing_metadata
        }

        verified_evidence.append(evidence_item)

        if not version or not publication_date:
            review_reasons.append(
                f"Result {index}: source version or "
                "publication date is unavailable."
            )

        if relevance_ratio < 0.2:
            review_reasons.append(
                f"Result {index}: low keyword overlap; "
                "manual relevance review is needed."
            )

    # Step 5: Determine the review status
    if not verified_evidence:
        review_required = True
        status = "no_usable_evidence"
        review_reasons.append(
            "No usable evidence was available."
        )
    elif review_reasons:
        review_required = True
        status = "review_required"
    else:
        review_required = False
        status = "basic_checks_passed"

    return {
        "status": status,
        "question": question,
        "evidence": verified_evidence,
        "review_required": review_required,
        "review_reasons": review_reasons,
        "limitations": [
            "Keyword overlap is not semantic or clinical validation.",
            "Source authenticity and medical correctness are not verified.",
            "A human reviewer must assess evidence before clinical use."
        ]
    }


if __name__ == "__main__":

    # Synthetic data for software testing only
    sample_question = (
        "Find the section that mentions asthma "
        "in the demonstration document."
    )

    sample_documents = [
        {
            "text": (
                "The term asthma appears in this synthetic "
                "document for retrieval testing only."
            ),
            "source": "healthcare_demo_guideline_synthetic.pdf",
            "page": 2,
            "version": "1.0",
            "publication_date": "2026-10-27"
        },
        {
            "text": (
                "A retrieval system should record source "
                "metadata and page numbers."
            ),
            "source": "healthcare_demo_guideline_synthetic.pdf",
            "page": 3,
            "version": "1.0",
            "publication_date": "2026-10-27"
        }
    ]

    result = evidence_quality_agent(
        sample_question,
        sample_documents
    )

    print("\n===== EVIDENCE QUALITY RESULT =====")
    print("Status:", result["status"])
    print("Review required:", result["review_required"])

    print("\nEvidence checks:")

    for item in result["evidence"]:
        print(f"\nResult: {item['result_number']}")
        print(f"Source: {item['source']}")
        print(f"Page: {item['page']}")
        print(
            "Keyword relevance:",
            item["keyword_relevance_ratio"]
        )
        print("Text:", item["text"])

    print("\nReview reasons:")

    for reason in result["review_reasons"]:
        print("-", reason)
