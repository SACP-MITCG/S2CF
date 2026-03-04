"""Chat session model for conversation history."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class ChatSession(db.Model):
    """Represents a chat session with message history."""

    __tablename__ = "chat_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=True)
    user_id = db.Column(db.String(255), nullable=True)
    messages = db.Column(JSONB, default=list)  # Backup of chat history
    metadata_ = db.Column("metadata", JSONB, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ChatSession {self.id}>"

    def to_dict(self) -> dict:
        """Serialize session to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "messages": self.messages or [],
            "metadata": self.metadata_ or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session history."""
        if self.messages is None:
            self.messages = []
        self.messages = self.messages + [{
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }]
        db.session.commit()

    @classmethod
    def create(
        cls,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> "ChatSession":
        """Create a new chat session."""
        session = cls(document_id=document_id, user_id=user_id)
        db.session.add(session)
        db.session.commit()
        return session

    @classmethod
    def get_by_id(cls, session_id: str) -> Optional["ChatSession"]:
        """Get session by ID."""
        return cls.query.get(session_id)

    @classmethod
    def get_or_create(cls, session_id: str, document_id: Optional[str] = None) -> "ChatSession":
        """Get existing session or create new one."""
        session = cls.query.get(session_id)
        if session is None:
            session = cls(id=session_id, document_id=document_id)
            db.session.add(session)
            db.session.commit()
        return session
