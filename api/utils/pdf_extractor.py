"""
Extracts plain text from PDF bytes using PyMuPDF (already in requirements).
Digital PDFs have embedded text — no OCR needed.
"""

import fitz  # pymupdf


def extract_pdf_text(pdf_bytes: bytes) -> str:
    extracted_pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if text:
                extracted_pages.append(f"[Page {i}]\n{text}")

    if not extracted_pages:
        return "No readable text found in this PDF. It may be a scanned image."

    return "\n\n".join(extracted_pages)
