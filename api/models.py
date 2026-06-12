from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from api.database import Base


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    username       = Column(String, nullable=False, index=True)
    email          = Column(String(255), unique=True, index=True, nullable=False)
    password_hash  = Column(String(255), nullable=True)
    oauth_provider = Column(String(80),  nullable=True)
    oauth_id       = Column(String(255), nullable=True)
    auth_type      = Column(String(20),  default="local", nullable=False)
    created_at     = Column(DateTime,    default=_now, nullable=False)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "chat_sessions"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title      = Column(String(255), default="New Conversation", nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    user     = relationship("User", back_populates="sessions")
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )


class Message(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    timestamp  = Column(DateTime, default=_now, nullable=False)

    session = relationship("Session", back_populates="messages")
