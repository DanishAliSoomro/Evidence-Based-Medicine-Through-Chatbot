from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Standard health check endpoint.
    """
    return {
        "status": "online",
        "message": "Hello! The Medical GraphRAG API is running and ready for your requests.",
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """
    Basic hello world route at the root.
    """
    return {"message": "Welcome to the Medical GraphRAG API. Visit /docs for documentation."}
