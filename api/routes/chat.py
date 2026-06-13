from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user
from api.models import Message
from api.schemas import ChatRequest, ChatResponse, SessionResponse, ChatMessage, SessionUpdate
from api.services.graph_rag_service import GraphRAGService
from api.repositories.chat_history_repo import ChatHistoryRepository

router = APIRouter()


def get_chat_repo(db: AsyncSession = Depends(get_db)):
    return ChatHistoryRepository(db)


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    user_id: int = Depends(get_current_user),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    return await repo.list_sessions(user_id=user_id)


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    user_id: int = Depends(get_current_user),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    return await repo.create_session("New Conversation", user_id=user_id)


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
async def rename_session(
    session_id: int,
    payload: SessionUpdate,
    user_id: int = Depends(get_current_user),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="A non-empty title is required.")

    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your session.")

    return await repo.update_session(session_id, payload.title.strip())


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    user_id: int = Depends(get_current_user),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your session.")

    await repo.delete_session(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(
    session_id: int,
    user_id: int = Depends(get_current_user),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your session.")

    return await repo.get_session_messages(session_id)


@router.post("/chat/test", response_model=ChatResponse)
async def chat_test(request: ChatRequest):
    with GraphRAGService() as service:
        service.conversation_history = [{"role": m.role, "content": m.content} for m in request.history]
        answer = service.perform_graph_rag(request.query)
        return ChatResponse(answer=answer, session_id=0, source_nodes=[])


@router.post("/chat", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    user_id: int = Depends(get_current_user),
    repo: ChatHistoryRepository = Depends(get_chat_repo),
):
    session_id = request.session_id
    if session_id is None:
        new_session = await repo.create_session(
            title=f"Chat: {request.query[:30]}...",
            user_id=user_id,
        )
        session_id = new_session.id
    else:
        session = await repo.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not your session.")

    history_records = await repo.get_session_messages(session_id)
    llm_history = [{"role": m.role, "content": m.content} for m in history_records]

    # Always save the user message first
    await repo.save_messages([
        Message(session_id=session_id, role="user", content=request.query),
    ])

    # Attempt GraphRAG — fall back gracefully if Neo4j or LLM is unavailable
    try:
        with GraphRAGService() as service:
            service.conversation_history = llm_history
            answer = service.perform_graph_rag(request.query)
    except Exception as e:
        answer = (
            "The knowledge service is currently unavailable. "
            "Your message has been saved and will be answered once the service is restored."
        )

    await repo.save_messages([
        Message(session_id=session_id, role="assistant", content=answer),
    ])

    return ChatResponse(answer=answer, session_id=session_id, source_nodes=[])
