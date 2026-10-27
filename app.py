import json
from pathlib import Path

import requests
import streamlit as st


# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Healthcare Agentic AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent

PDF_DIR = (
    BASE_DIR
    / "sources"
    / "medical_documents"
)

API_URL = "http://127.0.0.1:8000"


# ==================================================
# PROFESSIONAL UI DESIGN
# ==================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f7fb;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(120deg, #102a43, #176b87);
        padding: 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white;
        font-size: 32px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #e0f2fe;
        font-size: 15px;
        margin-bottom: 0;
    }

    .section-heading {
        color: #12344d;
        font-size: 23px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .notice {
        background: #fff7ed;
        border-left: 5px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    div.stButton > button[kind="primary"] {
        background-color: #176b87;
        color: white;
        border-radius: 10px;
        min-height: 45px;
        border: none;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #102a43;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏥 Healthcare Agentic AI</h1>
        <p>
            Multi-Agent Evidence Retrieval,
            Clinical Safety Review and Summary Generation
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="notice">
        <b>Important:</b> Educational prototype only.
        This application does not diagnose diseases or recommend treatment.
        Use synthetic test documents and data only.
        Clinical review is required.
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("⚙️ Control Panel")

    st.markdown("### Backend Connection")

    if st.button(
        "Check Backend",
        use_container_width=True,
    ):
        try:
            response = requests.get(
                f"{API_URL}/health",
                timeout=5,
            )

            if response.ok:
                st.success("Backend is connected.")
            else:
                st.error("Backend returned an error.")

        except requests.RequestException:
            st.error(
                "Backend is offline. Start FastAPI first."
            )

    st.divider()

    st.markdown("### Project Modules")

    st.markdown(
        """
        - Intake Agent
        - Patient Context Agent
        - Document Retrieval
        - Evidence Quality Agent
        - Safety Agent
        - Summary Agent
        - Output Validator
        """
    )

    st.divider()

    st.link_button(
        "Open API Documentation",
        f"{API_URL}/docs",
        use_container_width=True,
    )


# ==================================================
# SECTION 1: PDF UPLOAD
# ==================================================

st.markdown(
    '<div class="section-heading">01 · Upload Documents</div>',
    unsafe_allow_html=True,
)

st.write(
    "Upload PDF documents directly from your computer. "
    "The backend will use PDFs saved in the project document folder."
)

uploaded_files = st.file_uploader(
    "Choose PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
    help="You can select multiple PDF files.",
)

if uploaded_files:

    st.write(f"Selected files: {len(uploaded_files)}")

    for uploaded_file in uploaded_files:
        st.write(
            f"📄 {uploaded_file.name} "
            f"({uploaded_file.size / 1024:.1f} KB)"
        )

    if st.button(
        "📥 Upload PDFs",
        type="primary",
        use_container_width=True,
    ):

        PDF_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        saved_files = []
        failed_files = []

        for uploaded_file in uploaded_files:

            # Basic filename safety check.
            filename = Path(uploaded_file.name).name

            if not filename.lower().endswith(".pdf"):
                failed_files.append(
                    f"{filename}: Only PDF files are allowed."
                )
                continue

            # Limit each upload to 20 MB.
            if uploaded_file.size > 20 * 1024 * 1024:
                failed_files.append(
                    f"{filename}: File exceeds the 20 MB limit."
                )
                continue

            destination = PDF_DIR / filename

            try:
                file_bytes = uploaded_file.getvalue()

                # Basic PDF signature check.
                if not file_bytes.startswith(b"%PDF-"):
                    failed_files.append(
                        f"{filename}: File is not a valid PDF file."
                    )
                    continue

                # Save PDF into the project document directory.
                destination.write_bytes(file_bytes)

                saved_files.append(filename)

            except OSError as error:
                failed_files.append(
                    f"{filename}: {error}"
                )

        if saved_files:
            st.success(
                f"Uploaded successfully: {len(saved_files)} file(s)."
            )

            for filename in saved_files:
                st.write(f"✅ {filename}")

            st.info(
                "Documents are saved. Click Run Healthcare Workflow "
                "below to rebuild the local vector database and "
                "search the documents."
            )

        if failed_files:
            st.error("Some files could not be uploaded.")

            for error in failed_files:
                st.write(f"❌ {error}")


# Show files already available to the backend.

with st.expander("📚 View available PDF documents"):

    if PDF_DIR.exists():

        pdf_files = sorted(PDF_DIR.glob("*.pdf"))

        if pdf_files:
            for pdf_file in pdf_files:
                st.write(f"📄 {pdf_file.name}")
        else:
            st.info("No PDF documents are currently available.")

    else:
        st.info(
            "The document folder will be created when you upload a PDF."
        )


# ==================================================
# SECTION 2: EVIDENCE SEARCH
# ==================================================

st.markdown(
    '<div class="section-heading">02 · Evidence Search</div>',
    unsafe_allow_html=True,
)

user_request = st.text_area(
    "Enter your search question",
    value=(
        "Find the section that mentions asthma "
        "in the demonstration document."
    ),
    height=100,
    placeholder="Enter a question about your uploaded documents...",
)


# ==================================================
# SECTION 3: PATIENT CONTEXT
# ==================================================

st.markdown(
    '<div class="section-heading">03 · Patient Context</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Use synthetic test information only. "
    "Blank fields mean unknown, not a confirmed absence."
)

col1, col2 = st.columns(2)

with col1:

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=35,
        step=1,
    )

    condition = st.text_input(
        "Documented condition",
        value="Asthma",
    )

    medications = st.text_input(
        "Current medications",
        placeholder="Leave blank if unknown",
    )

with col2:

    symptoms = st.text_input(
        "Reported symptoms",
        value="Worsening cough",
    )

    allergies = st.text_input(
        "Allergies",
        placeholder="Leave blank if unknown",
    )

    vitals = st.text_input(
        "Vital signs",
        placeholder="Leave blank if unknown",
    )


# ==================================================
# SECTION 4: RUN WORKFLOW
# ==================================================

st.markdown(
    '<div class="section-heading">04 · Run Agent Workflow</div>',
    unsafe_allow_html=True,
)

if st.button(
    "🚀 Run Healthcare Workflow",
    type="primary",
    use_container_width=True,
):

    if not user_request.strip():

        st.error("Please enter a search question.")

    else:

        patient_data = {
            "age": int(age) if age > 0 else None,

            "documented_conditions": (
                [condition.strip()]
                if condition.strip()
                else None
            ),

            "reported_symptoms": (
                [symptoms.strip()]
                if symptoms.strip()
                else None
            ),

            "current_medications": (
                medications.strip() or None
            ),

            "allergies": allergies.strip() or None,

            "vital_signs": (
                vitals.strip() or None
            ),
        }

        payload = {
            "user_request": user_request.strip(),
            "patient_data": patient_data,
        }

        try:

            with st.spinner(
                "Loading documents and running agents..."
            ):

                response = requests.post(
                    f"{API_URL}/run",
                    json=payload,
                    timeout=300,
                )

            if response.ok:

                api_result = response.json()

                st.session_state["last_api_result"] = (
                    api_result
                )

                st.success(
                    "Workflow request completed successfully."
                )

            else:

                st.error(
                    f"API error: HTTP {response.status_code}"
                )

                try:
                    st.json(response.json())
                except ValueError:
                    st.text(response.text)

        except requests.Timeout:

            st.error(
                "The request timed out. Check the backend terminal."
            )

        except requests.RequestException as error:

            st.error(
                "Cannot connect to FastAPI. Make sure the backend "
                "is running."
            )

            st.caption(str(error))


# ==================================================
# SECTION 5: DISPLAY RESULTS
# ==================================================

api_result = st.session_state.get("last_api_result")

if api_result:

    workflow = api_result.get(
        "workflow_result",
        {},
    )

    summary_result = workflow.get(
        "summary",
        {},
    )

    summary = summary_result.get(
        "summary",
        {},
    )

    st.divider()

    st.markdown(
        '<div class="section-heading">05 · Workflow Dashboard</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Workflow Status",
            workflow.get("status", "Unknown"),
        )

    with col2:
        st.metric(
            "Retrieved Evidence",
            len(
                workflow.get("evidence", {}).get(
                    "evidence",
                    [],
                )
            ),
        )

    with col3:
        st.metric(
            "Clinical Review",
            "Required",
        )

    st.caption(
        "Workflow completion does not establish medical accuracy."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📄 Summary",
            "🔎 Evidence",
            "🤖 Agent Status",
            "🧾 Full Response",
        ]
    )

    # ----------------------------------------------
    # SUMMARY TAB
    # ----------------------------------------------

    with tab1:

        st.subheader("Patient Context")

        st.json(
            summary.get(
                "patient_context",
                {},
            )
        )

        st.subheader("Missing Information")

        missing = summary.get(
            "missing_information",
            [],
        )

        if missing:

            for item in missing:
                st.warning(str(item))

        else:
            st.write("No missing fields reported.")

        st.subheader("Review Reasons")

        reasons = summary.get(
            "review_reasons",
            [],
        )

        if reasons:

            for reason in reasons:
                st.warning(str(reason))

        else:

            st.info(
                "No review reasons were reported by the current checks. "
                "This does not establish clinical validity."
            )

        st.info(
            summary.get(
                "disclaimer",
                "Human review is required.",
            )
        )

    # ----------------------------------------------
    # EVIDENCE TAB
    # ----------------------------------------------

    with tab2:

        st.subheader("Retrieved Evidence")

        evidence_items = summary.get(
            "evidence_summary",
            [],
        )

        unique_items = []
        seen = set()

        for item in evidence_items:

            text = item.get("text", "")

            normalized = " ".join(
                text.split()
            ).casefold()

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_items.append(item)

        if unique_items:

            st.caption(
                f"Displaying {len(unique_items)} unique text entries."
            )

            for index, item in enumerate(
                unique_items,
                start=1,
            ):

                source = item.get(
                    "source",
                    "Unknown source",
                )

                page = item.get(
                    "page",
                    "Unknown",
                )

                with st.expander(
                    f"Evidence {index} · {source} · Page {page}"
                ):

                    st.write(
                        "**Version:**",
                        item.get("version") or "Unknown",
                    )

                    st.write(
                        "**Document date:**",
                        item.get("publication_date") or "Unknown",
                    )

                    st.text(
                        item.get("text", "")
                    )

        else:

            st.info("No evidence was retrieved.")

        st.warning(
            "Retrieved passages are not proof of medical correctness."
        )

    # ----------------------------------------------
    # AGENT STATUS TAB
    # ----------------------------------------------

    with tab3:

        st.subheader("Agent Execution Details")

        agent_keys = [
            ("intake", "Intake Agent"),
            ("patient_context", "Patient Context Agent"),
            ("evidence", "Evidence Quality Agent"),
            ("safety", "Safety Agent"),
            ("summary", "Summary Agent"),
            ("validation", "Output Validator"),
        ]

        for key, label in agent_keys:

            with st.expander(label):

                result = workflow.get(key)

                if isinstance(result, dict):
                    st.json(result)

                elif result is None:
                    st.write("No result available.")

                else:
                    st.write(result)

    # ----------------------------------------------
    # FULL RESPONSE TAB
    # ----------------------------------------------

    with tab4:

        st.subheader("Complete API Response")

        st.json(api_result)

        st.download_button(
            "📥 Download JSON Result",
            data=json.dumps(
                api_result,
                indent=2,
                ensure_ascii=False,
            ),
            file_name="healthcare_workflow_result.json",
            mime="application/json",
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Healthcare Agentic AI | Educational Prototype | "
    "Not for Clinical Diagnosis or Treatment"
)