import fitz  # PyMuPDF
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF.
    Handles text-heavy and table-heavy documents.
    Returns concatenated text from all pages.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found at path: {file_path}")

    doc = fitz.open(file_path)
    full_text = []

    for page_num, page in enumerate(doc, start=1):
        # Extract text preserving layout (better for tables)
        text = page.get_text("text")
        if text.strip():
            full_text.append(f"--- Page {page_num} ---\n{text}")

    doc.close()

    if not full_text:
        raise ValueError("No extractable text found in PDF. It may be scanned/image-based.")

    return "\n\n".join(full_text)


def chunk_text(text: str, max_chars: int = 12000) -> str:
    """
    Truncate text to fit within LLM context limits.
    12000 chars is safe for Groq's context window while keeping costs low.
    In later phases this becomes proper semantic chunking.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Document truncated for extraction]"
