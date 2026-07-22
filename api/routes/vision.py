import tempfile
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from api.dependencies import get_current_user
from api.utils.classifier import classify_document
from api.utils.pdf_extractor import extract_pdf_text

router = APIRouter()


# ── PDF test ──────────────────────────────────────────────────────

class PdfResponse(BaseModel):
    extracted_text: str
    page_count: int
    is_medical: bool
    confidence: str
    reason: str
    verdict: str


@router.post("/pdf/test", response_model=PdfResponse, tags=["Vision"])
async def test_pdf(file: UploadFile = File(...)):
    """Upload a PDF file — get back extracted text + medical classification verdict."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF.")
    pdf_bytes = await file.read()
    try:
        text = extract_pdf_text(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"PDF extraction error: {str(e)}")
    try:
        result = classify_document(text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Classification error: {str(e)}")
    page_count = text.count("[Page ")
    verdict = "Medical — usable as context" if result["is_medical"] else "Not medical — rejected"
    return PdfResponse(
        extracted_text=text[:2000],
        page_count=page_count,
        is_medical=result["is_medical"],
        confidence=result["confidence"],
        reason=result["reason"],
        verdict=verdict,
    )


# ── PDF upload → read-only context ───────────────────────────────

class UploadPdfResponse(BaseModel):
    status: str
    filename: str
    message: str
    pdf_text: str


@router.post("/upload/pdf", response_model=UploadPdfResponse, tags=["Upload"])
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
):
    """
    Upload a medical PDF — extracts the text and returns it to the client.
    The client attaches it as context on subsequent chat messages.
    Nothing is written to Neo4j.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    pdf_bytes = await file.read()

    try:
        text = extract_pdf_text(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"PDF extraction error: {str(e)}")

    try:
        result = classify_document(text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Classification error: {str(e)}")

    if not result["is_medical"]:
        raise HTTPException(
            status_code=400,
            detail=f"This PDF does not appear to be a medical document. Reason: {result['reason']}",
        )

    return UploadPdfResponse(
        status="ready",
        filename=file.filename,
        message=f"PDF loaded — ask any question about it.",
        pdf_text=text,
    )
