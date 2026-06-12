# TODO: the ingest service is not implemented properly but currenlty not tested.
# from fastapi import APIRouter, Depends, BackgroundTasks
# from api.schemas import ProcessRequest, ProcessResponse
# from api.repositories.graph_repo import GraphRepository
# from api.services.extraction_service import ExtractionService
# from api.services.process_service import ProcessService
# import os

# router = APIRouter()

# def get_process_service():
#     repo = GraphRepository()
#     extract_svc = ExtractionService()
#     try:
#         yield ProcessService(repo, extract_svc)
#     finally:
#         repo.close()

# @router.post("/ingest", response_model=ProcessResponse)
# async def process_documents(
#     request: ProcessRequest, 
#     background_tasks: BackgroundTasks,
#     service: ProcessService = Depends(get_process_service)
# ):
#     """
#     Triggers PDF processing. This runs in the background to avoid timeout.
#     """
#     directory = request.directory_path or r"D:\Volume C\Gotharo Data\Labeled Dataset"
    
#     if not os.path.exists(directory):
#         return ProcessResponse(status="error", files_processed=0, message=f"Directory {directory} not found.")

#     # Add the long-running task to background tasks
#     background_tasks.add_task(service.process_directory, directory)
    
#     return ProcessResponse(
#         status="accepted",
#         files_processed=0,
#         message=f"Processing started for directory: {directory}. This will run in the background."
#     )

from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.schemas import PMCIngestRequest, PMCIngestStatusResponse, ProcessResponse
from api.services.pmc_ingestion_service import (
    DEFAULT_CHECKPOINT,
    DEFAULT_ROOT,
    checkpoint_summary,
    discover_jobs,
    init_checkpoint,
    run_pmc_ingestion,
)


router = APIRouter()


@router.post("/ingest/pmc", response_model=ProcessResponse)
async def ingest_pmc_articles(request: PMCIngestRequest, background_tasks: BackgroundTasks):
    """
    Starts PMC PDF ingestion as a background job.
    Uses PDFProcessingService, which uses PDFExtractor, TextChunker, GraphRelationExtractor,
    and Neo4jRepository.
    """
    root = Path(request.root_path).resolve() if request.root_path else DEFAULT_ROOT.resolve()
    checkpoint = Path(request.checkpoint_path).resolve() if request.checkpoint_path else DEFAULT_CHECKPOINT.resolve()

    if not root.exists():
        raise HTTPException(status_code=404, detail=f"PMC root not found: {root}")

    init_checkpoint(checkpoint)
    jobs = discover_jobs(root, request.folders)
    if request.limit_pdfs is not None:
        jobs = jobs[:request.limit_pdfs]

    background_tasks.add_task(
        run_pmc_ingestion,
        root=root,
        checkpoint=checkpoint,
        folders=request.folders,
        max_workers=request.max_workers,
        limit_pdfs=request.limit_pdfs,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
        iter_size=request.iter_size,
        retry_failed=request.retry_failed,
        clean=request.clean_checkpoint,
    )

    return ProcessResponse(
        status="accepted",
        files_processed=0,
        message=f"PMC ingestion queued for {len(jobs)} PDF(s) from first {request.folders} folder(s).",
    )


@router.get("/ingest/pmc/status", response_model=PMCIngestStatusResponse)
async def get_pmc_ingestion_status(checkpoint_path: str | None = None):
    checkpoint = Path(checkpoint_path).resolve() if checkpoint_path else DEFAULT_CHECKPOINT.resolve()
    return PMCIngestStatusResponse(status_counts=checkpoint_summary(checkpoint))


