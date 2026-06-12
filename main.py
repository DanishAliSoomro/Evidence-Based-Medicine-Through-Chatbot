from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, health
from api.database import engine, Base

app = FastAPI(
    title="Medical GraphRAG API",
    description="A Graph-based Retrieval Augmented Generation API for Medical Data",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
# app.include_router(ingest.router, prefix="/api", tags=["Ingest"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # In case you want to start fresh
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
