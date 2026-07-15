from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user
from api.repositories.chat_history_repo import ChatHistoryRepository
from api.schemas import LoginRequest, UserCreate, UserResponse, TokenResponse, UsernameUpdate
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


@router.patch("/users/me", response_model=UserResponse)
async def update_username(
    payload: UsernameUpdate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ChatHistoryRepository(db)
    user = await repo.update_username(user_id, payload.username.strip())
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ChatHistoryRepository(db)
    deleted = await repo.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
