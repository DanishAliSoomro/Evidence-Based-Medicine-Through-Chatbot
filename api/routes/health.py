import json
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from config import settings
from api.services.prompts import GUARDRAIL, PICO_Rules
from api.services.graph_rag_service import GraphRAGService

router = APIRouter()


class PicoTestRequest(BaseModel):
    query: str


class PicoTestResponse(BaseModel):
    guardrail_class: str
    pico_status: str
    pico_elements: str
    query_used: str
    answer: str


def _llm():
    return OpenAI(base_url=settings.AZURE_OPENAI_ENDPOINT, api_key=settings.AZURE_OPENAI_KEY)


def _run_guardrail(client, query: str) -> str:
    raw = client.chat.completions.create(
        model=settings.AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": GUARDRAIL},
            {"role": "user",   "content": query},
        ],
        temperature=0,
        max_tokens=20,
    ).choices[0].message.content.strip()
    try:
        return json.loads(raw).get("class", "medical")
    except Exception:
        return "medical"


def _run_pico(client, query: str) -> dict:
    raw = client.chat.completions.create(
        model=settings.AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": PICO_Rules},
            {"role": "user",   "content": query},
        ],
        temperature=0,
        max_tokens=300,
    ).choices[0].message.content.strip()

    status = "VALID" if "Status: VALID" in raw else "INVALID"

    structured = query
    if status == "VALID":
        lines = {l.split(":")[0].strip(): l.split(":", 1)[1].strip()
                 for l in raw.splitlines() if ":" in l and l.split(":")[0].strip() in ("P", "I", "C", "O")}

        def _val(k):
            v = lines.get(k, "")
            return v if v and "<MISSING>" not in v else ""

        parts = [f"In {_val('P')}" if _val("P") else "",
                 f"does {_val('I')}" if _val("I") else "",
                 f"compared to {_val('C')}" if _val("C") else "",
                 f"improve {_val('O')}" if _val("O") else ""]
        structured = " ".join(p for p in parts if p) + "?"

    return {"status": status, "elements": raw, "structured_query": structured}


@router.get("/health")
async def health_check():
    return {
        "status": "online",
        "message": "EBM GraphRAG API is running.",
        "version": "1.0.0"
    }


@router.get("/")
async def root():
    return {"message": "Welcome to the Medical GraphRAG API. Visit /docs for documentation."}


@router.post("/chat/pico_valid", response_model=PicoTestResponse, tags=["Test"])
async def pico_valid_test(request: PicoTestRequest):
    """Full pipeline test: GUARDRAIL → PICO_Rules → GraphRAG. Shows each step's result."""
    client = _llm()

    # Step 1 — Guardrail (2-class: medical / off_topic)
    guardrail_class = _run_guardrail(client, request.query)
    if guardrail_class == "off_topic":
        return PicoTestResponse(
            guardrail_class=guardrail_class,
            pico_status="SKIPPED",
            pico_elements="",
            query_used=request.query,
            answer="I can only assist with medical and clinical questions.",
        )

    # Step 2 — PICO extraction
    pico = _run_pico(client, request.query)
    query_used = pico["structured_query"]

    # Step 3 — GraphRAG
    with GraphRAGService() as service:
        answer = service.perform_graph_rag(query_used)

    return PicoTestResponse(
        guardrail_class=guardrail_class,
        pico_status=pico["status"],
        pico_elements=pico["elements"],
        query_used=query_used,
        answer=answer,
    )
