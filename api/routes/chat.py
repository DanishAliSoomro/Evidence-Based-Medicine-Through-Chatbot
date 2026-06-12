from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models import Message
from api.schemas import ChatRequest, ChatResponse, SessionResponse, ChatMessage
from api.services.graph_rag_service import GraphRAGService
from api.repositories.chat_history_repo import ChatHistoryRepository

router = APIRouter()

# Dependency for ChatHistoryRepository
def get_chat_repo(db: AsyncSession = Depends(get_db)):
    return ChatHistoryRepository(db)

@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    owner_id: Optional[int] = Query(default=None),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    """
    Returns all chat sessions using injected repository.
    """
    return await repo.list_sessions(user_id=owner_id)

@router.post("/sessions", response_model=SessionResponse)
async def create_session(repo: ChatHistoryRepository = Depends(get_chat_repo)):
    """
    Creates a new chat session manually using injected repository.
    """
    return await repo.create_session("New Conversation")

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(
    session_id: int, 
    repo: ChatHistoryRepository = Depends(get_chat_repo)
):
    """
    Retrieves all messages for a specific session ID using injected repository.
    """
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return await repo.get_session_messages(session_id)

@router.post("/chat/test", response_model=ChatResponse)
async def chat_test(request: ChatRequest):
    """
    Stateless chat endpoint for quick testing.
    Ignores the database and session history.
    """
    with GraphRAGService() as service:
        # Load history from request (stateless)
        service.conversation_history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Perform the GraphRAG query
        answer = service.perform_graph_rag(request.query)
        
        return ChatResponse(
            answer=answer,
            session_id=0,
            source_nodes=[]
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest, 
    repo: ChatHistoryRepository = Depends(get_chat_repo)
):
    """
    Stateful chat endpoint using injected repository and service layers.
    """
    # 1. Determine Session ID (Create if missing)
    session_id = request.session_id
    if session_id is None:
        new_session = await repo.create_session(
            title=f"Chat: {request.query[:30]}...",
            user_id=request.owner_id,
        )
        session_id = new_session.id
    else:
        # Verify existing session
        session = await repo.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat Session not found.")
        if request.owner_id is not None and session.user_id not in (None, request.owner_id):
            raise HTTPException(status_code=403, detail="Chat Session does not belong to this user.")
        session_id = session.id

    # 2. Fetch history from Repository
    history_records = await repo.get_session_messages(session_id)
    
    # Format history for LLM
    llm_history = [{"role": m.role, "content": m.content} for m in history_records]

    # 3. Perform GraphRAG
    with GraphRAGService() as service:
        service.conversation_history = llm_history
        answer = service.perform_graph_rag(request.query)

    # 4. Save both messages to DB
    await repo.save_messages([
        Message(session_id=session_id, role="user", content=request.query),
        Message(session_id=session_id, role="assistant", content=answer)
    ])

    return ChatResponse(
        answer=answer,
        session_id=session_id,
        source_nodes=[]
    )
