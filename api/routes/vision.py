import base64
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from api.utils.vision import describe_image
from api.utils.classifier import classify_document
from api.utils.pdf_extractor import extract_pdf_text

router = APIRouter()


# ── Image test ────────────────────────────────────────────────────────────────

class VisionResponse(BaseModel):
    description: str


@router.post("/vision/test", response_model=VisionResponse, tags=["Vision"])
async def test_vision(file: UploadFile = File(...)):
    """Upload an image file — get back the GPT-4o mini text description."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{b64}"

    try:
        description = describe_image(data_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Vision model error: {str(e)}")

    return VisionResponse(description=description)


# ── PDF test ──────────────────────────────────────────────────────────────────

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

    # Only ingest if medical AND high confidence
    should_ingest = result["is_medical"] and result["confidence"] == "high"
    verdict = "Ingest into Neo4j" if should_ingest else "Skip Neo4j — use as context only"

    page_count = text.count("[Page ")
    return PdfResponse(
        extracted_text=text[:2000],  # preview first 2000 chars so response stays readable
        page_count=page_count,
        is_medical=result["is_medical"],
        confidence=result["confidence"],
        reason=result["reason"],
        verdict=verdict,
    )
