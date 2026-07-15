from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models import Message, Session, User


class ChatHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ users

    async def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_users(self) -> List[User]:
        result = await self.db.execute(select(User).order_by(User.id.asc()))
        return list(result.scalars().all())

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def update_username(self, user_id: int, username: str) -> Optional[User]:
        user = await self.db.get(User, user_id)
        if not user:
            return None
        user.username = username
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        user = await self.db.get(User, user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def login_user(self, identifier: str, password_hash: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where((User.username == identifier) | (User.email == identifier))
        )
        user = result.scalar_one_or_none()
        if not user or user.password_hash != password_hash:
            return None
        return user

    # ------------------------------------------------------------ sessions

    async def list_sessions(self, user_id: Optional[int] = None) -> List[Session]:
        query = select(Session).order_by(Session.created_at.desc())
        if user_id is not None:
            query = query.where(Session.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_session(
        self,
        title: str = "New Conversation",
        user_id: Optional[int] = None,
    ) -> Session:
        session = Session(title=title, user_id=user_id)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: int) -> Optional[Session]:
        result = await self.db.execute(
            select(Session)
            .options(selectinload(Session.messages))
            .where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_session(self, session_id: int, title: str) -> Optional[Session]:
        session = await self.db.get(Session, session_id)
        if not session:
            return None
        session.title = title
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def delete_session(self, session_id: int) -> bool:
        await self.db.execute(delete(Message).where(Message.session_id == session_id))
        result = await self.db.execute(delete(Session).where(Session.id == session_id))
        await self.db.commit()
        return result.rowcount > 0

    # ----------------------------------------------------------- messages

    async def get_session_messages(self, session_id: int) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.id.asc())
        )
        return list(result.scalars().all())

    async def save_messages(self, messages: List[Message]) -> None:
        if not messages:
            return
        self.db.add_all(messages)
        await self.db.commit()

    async def delete_all_user_sessions(self, user_id: int) -> int:
        session_ids_result = await self.db.execute(
            select(Session.id).where(Session.user_id == user_id)
        )
        session_ids = [row[0] for row in session_ids_result.fetchall()]
        if not session_ids:
            return 0
        await self.db.execute(delete(Message).where(Message.session_id.in_(session_ids)))
        result = await self.db.execute(delete(Session).where(Session.user_id == user_id))
        await self.db.commit()
        return result.rowcount
