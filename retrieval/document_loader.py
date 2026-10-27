
from pathlib import Path
import re
import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ==============================
# 1. PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_DIR = BASE_DIR / "sources" / "medical_documents"
DB_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "healthcare_evidence"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ==============================
# 2. EXTRACT PDF METADATA
# ==============================

def extract_metadata(text: str) -> dict:
    """Extract version and document date from PDF text."""

    version_match = re.search(
        r"Version:\s*([^\r\n]+)",
        text,
        re.IGNORECASE,
    )

    date_match = re.search(
        r"Document date:\s*([^\r\n]+)",
        text,
        re.IGNORECASE,
    )

    version = (
        version_match.group(1).strip()
        if version_match
        else None
    )

    publication_date = (
        date_match.group(1).strip()
        if date_match
        else None
    )

    return {
        "version": version,
        "publication_date": publication_date,
    }


# ==============================
# 3. LOAD MEDICAL PDF DOCUMENTS
# ==============================

def load_medical_pdfs():
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {PDF_DIR}\n"
            "Place a PDF inside sources/medical_documents."
        )

    documents = []

    for pdf_path in pdf_files:
        print(f"\nLoading PDF: {pdf_path.name}")

        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()

        if not pages:
            print(f"Warning: No pages extracted from {pdf_path.name}")
            continue

        full_text = "\n".join(
            page.page_content for page in pages
        )

        metadata = extract_metadata(full_text)

        for page in pages:
            # Preserve the original PDF page index.
            page.metadata["source"] = pdf_path.name

            # Add metadata only when available.
            if metadata["version"] is not None:
                page.metadata["version"] = metadata["version"]

            if metadata["publication_date"] is not None:
                page.metadata["publication_date"] = (
                    metadata["publication_date"]
                )

        documents.extend(pages)

        print(f"Pages loaded: {len(pages)}")
        print(f"Version: {metadata['version']}")
        print(f"Document date: {metadata['publication_date']}")

    if not documents:
        raise ValueError(
            "No readable PDF pages were found."
        )

    print(f"\nTotal pages loaded: {len(documents)}")

    return documents


# ==============================
# 4. SPLIT DOCUMENTS INTO CHUNKS
# ==============================

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
    )

    chunks = splitter.split_documents(documents)

    # Remove empty chunks.
    chunks = [
        chunk
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    # Remove exact duplicate chunks from the same source/page.
    unique_chunks = []
    seen_chunks = set()

    for chunk in chunks:
        source = chunk.metadata.get("source", "")
        page = chunk.metadata.get("page", "")
        normalized_text = " ".join(
            chunk.page_content.split()
        ).casefold()

        key = (source, page, normalized_text)

        if key in seen_chunks:
            continue

        seen_chunks.add(key)
        unique_chunks.append(chunk)

    print(f"Chunks before deduplication: {len(chunks)}")
    print(f"Unique chunks: {len(unique_chunks)}")

    return unique_chunks


# ==============================
# 5. CREATE VECTOR DATABASE
# ==============================

def create_vector_database(chunks):
    if not chunks:
        raise ValueError(
            "Cannot create a vector database without chunks."
        )

    # Rebuild the demo database from the current PDF files.
    # This prevents old indexed records from accumulating.
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)

    DB_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR),
        collection_name=COLLECTION_NAME,
    )

    print("Vector database rebuilt successfully.")

    return vector_db


# ==============================
# 6. RETRIEVE UNIQUE EVIDENCE
# ==============================

def retrieve_evidence(vector_db, question: str, k: int = 3):
    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "Search question cannot be empty."
        )

    if k < 1:
        raise ValueError("k must be at least 1.")

    # Fetch extra candidates so duplicates can be filtered.
    candidates = vector_db.similarity_search_with_score(
        question,
        k=max(k * 3, k),
    )

    unique_results = []
    seen_results = set()

    for document, score in candidates:
        source = document.metadata.get("source", "")
        page = document.metadata.get("page", "")

        normalized_text = " ".join(
            document.page_content.split()
        ).casefold()

        # Deduplicate identical content from the same source.
        key = (source, page, normalized_text)

        if key in seen_results:
            continue

        seen_results.add(key)
        unique_results.append((document, score))

        if len(unique_results) >= k:
            break

    print(f"Unique evidence results: {len(unique_results)}")

    return unique_results


# ==============================
# 7. TEST RETRIEVAL DIRECTLY
# ==============================

if __name__ == "__main__":

    try:
        documents = load_medical_pdfs()

        chunks = split_documents(documents)

        if not chunks:
            raise ValueError(
                "No readable text chunks found in the PDFs."
            )

        vector_db = create_vector_database(chunks)

        question = input(
            "\nEnter a healthcare evidence search question: "
        ).strip()

        if not question:
            raise ValueError(
                "Please enter a search question."
            )

        results = retrieve_evidence(
            vector_db,
            question,
            k=3,
        )

        print("\n===== RETRIEVED EVIDENCE =====")

        if not results:
            print("No matching evidence was retrieved.")

        for index, (document, score) in enumerate(
            results,
            start=1,
        ):
            metadata = document.metadata

            page_index = metadata.get("page")
            page_number = (
                page_index + 1
                if isinstance(page_index, int)
                else "Unknown"
            )

            print(f"\nResult {index}")
            print(f"Source: {metadata.get('source')}")
            print(f"Page: {page_number}")
            print(f"Version: {metadata.get('version', 'Unknown')}")
            print(
                "Document date: "
                f"{metadata.get('publication_date', 'Unknown')}"
            )
            print(f"Distance score: {score:.4f}")
            print("Text:")
            print(document.page_content[:700])
            print("-" * 60)

        print("\nRetrieval test completed.")

    except Exception as error:
        print("\nRetrieval failed.")
        print(f"Error: {error}")
        raise
