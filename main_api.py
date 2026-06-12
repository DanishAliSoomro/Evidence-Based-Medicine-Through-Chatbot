from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api.routes import chat, ingest, health
from api.database import engine, Base
import api.models  # noqa: F401 — registers models with SQLAlchemy metadata

app = FastAPI(
    title="Medical GraphRAG API",
    description="Graph-based Retrieval Augmented Generation API for Medical Data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized.")


app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router,   prefix="/api", tags=["Chat"])
app.include_router(ingest.router, prefix="/api", tags=["Ingest"])

frontend_dist = Path(__file__).parent / "Chat-Design" / "EBM Frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    print(f"Frontend mounted from: {frontend_dist}")
else:
    print(f"Warning: Frontend dist not found at {frontend_dist}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
