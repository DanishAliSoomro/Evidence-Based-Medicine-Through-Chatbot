from fastapi import HTTPException, status

from api.repositories.chat_history_repo import ChatHistoryRepository
from api.schemas import UserCreate, LoginRequest, UserResponse, TokenResponse
from api.utils.security import hash_password, create_token


class RegistryService:

    def __init__(self, repo: ChatHistoryRepository):
        self.repo = repo

    async def register(self, payload: UserCreate) -> TokenResponse:
        existing = await self.repo.get_user_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        user = await self.repo.create_user(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        return TokenResponse(
            access_token=create_token(user.id),
            user=UserResponse.model_validate(user),
        )

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.repo.login_user(
            identifier=payload.identifier,
            password_hash=hash_password(payload.password),
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )
        return TokenResponse(
            access_token=create_token(user.id),
            user=UserResponse.model_validate(user),
        )
