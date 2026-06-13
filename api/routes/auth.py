from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.repositories.chat_history_repo import ChatHistoryRepository
from api.schemas import LoginRequest, UserCreate, UserResponse, TokenResponse
from api.services.registry import RegistryService

router = APIRouter()


def get_registry(db: AsyncSession = Depends(get_db)) -> RegistryService:
    return RegistryService(ChatHistoryRepository(db))


@router.post("/users", response_model=TokenResponse, status_code=201)
async def register(payload: UserCreate, svc: RegistryService = Depends(get_registry)):
    return await svc.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, svc: RegistryService = Depends(get_registry)):
    return await svc.login(payload)
