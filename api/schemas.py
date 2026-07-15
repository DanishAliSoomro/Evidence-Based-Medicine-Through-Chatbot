from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: Optional[str] = None


class LoginRequest(BaseModel):
    identifier: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    user: UserResponse


class UsernameUpdate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)


class ChatMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    timestamp: datetime


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    title: str
    created_at: datetime


class SessionDetail(SessionResponse):
    messages: List[ChatMessage] = Field(default_factory=list)


class SessionCreate(BaseModel):
    title: str = "New Conversation"
    user_id: Optional[int] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[int] = None



class ChatResponse(BaseModel):
    answer: str
    session_id: int
    source_nodes: List[str] = Field(default_factory=list)


class ProcessRequest(BaseModel):
    directory_path: Optional[str] = None


class ProcessResponse(BaseModel):
    status: str
    files_processed: int
    message: str


class PMCIngestRequest(BaseModel):
    root_path: Optional[str] = None
    checkpoint_path: Optional[str] = None
    folders: int = 10
    max_workers: int = 1
    limit_pdfs: Optional[int] = None
    chunk_size: int = 1000
    chunk_overlap: int = 100
    iter_size: int = 4
    retry_failed: bool = False
    clean_checkpoint: bool = False


class PMCIngestStatusResponse(BaseModel):
    status_counts: dict[str, int]


class Chunk(BaseModel):
    chunk_id: str
    page_number: int
    content: str
    content_id: str
    embedding: list[float] | None = None


class Entity(BaseModel):
    name: str
    type: str
    description: str


class Relationship(BaseModel):
    source: str
    target: str
    description: str
    strength: int


class CombinedGraphChunk(BaseModel):
    id: str
    chunk: Chunk
    entities: List[Entity]
    relationships: List[Relationship]
    raw_output: str
    file_name: Optional[str] = None
