# Healthcare Agentic AI

A multi-agent healthcare document assistant designed to retrieve relevant information from uploaded healthcare documents, evaluate evidence quality, perform safety checks, and generate structured summaries.

> **Disclaimer:** This project is an educational demonstration. It is not intended for medical diagnosis, treatment recommendations, or emergency medical decisions.

## Project Overview

Healthcare information is often distributed across multiple documents. Finding relevant information and presenting it in a structured format can be time-consuming.

This project demonstrates an agent-based workflow that processes healthcare documents, retrieves relevant evidence, evaluates the available information, performs safety checks, and generates a structured response.

## Key Features

- PDF document upload and processing
- Document chunking and retrieval
- Multi-agent workflow orchestration
- Patient context processing
- Evidence quality checks
- Safety checks and human-review flags
- Structured summary generation
- Output validation
- FastAPI backend
- Streamlit user interface
- Automated tests

## Agent Architecture

1. **Intake Agent:** Processes the user's request.
2. **Patient Context Agent:** Handles available patient context.
3. **Evidence Quality Agent:** Performs basic checks on retrieved evidence.
4. **Safety Agent:** Identifies missing information and situations requiring human review.
5. **Summary Agent:** Generates a structured summary.
6. **Output Validator Agent:** Validates the workflow output.

## Technology Stack

- Python
- FastAPI
- Streamlit
- ChromaDB
- Document retrieval and embedding components
- Pytest

Confirm the exact embedding model, LLM provider, and package versions from the implementation before publishing.

## Project Structure

```text
healthcare_agentic_ai/
├── agents/
├── retrieval/
├── orchestration/
├── api/
├── sources/
│   └── medical_documents/
├── tests/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd healthcare_agentic_ai
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an appropriate terminal or resolve the execution-policy issue according to your system's security requirements.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Add demo documents

Place synthetic healthcare PDF documents in:

```text
sources/medical_documents/
```

Do not use real patient records in this public demo.

### 5. Run the workflow

```bash
python -m orchestration.orchestrator
```

### 6. Start the API

```bash
python -m uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

### 7. Start the frontend

Open another terminal and run:

```bash
python -m streamlit run app.py
```

## Testing

Run the automated tests:

```bash
python -m pytest tests/ -v
```

## Limitations

- Evidence quality checks do not establish clinical correctness.
- Retrieved documents may be incomplete or outdated.
- Generated summaries require appropriate human review.
- The system must not be used as a substitute for qualified medical professionals.
- Performance and answer quality should be evaluated with a defined test dataset before making reliability claims.

## Future Improvements

- Retrieval precision and recall evaluation
- Groundedness and answer relevance evaluation
- Improved document provenance and citation display
- Structured evaluation reports
- Authentication and access controls
- Production-grade logging and monitoring

## License

Add an appropriate license before distributing this repository.