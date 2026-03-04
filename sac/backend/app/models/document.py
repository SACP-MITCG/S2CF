"""Document model for uploaded documents and imported IRMs."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class Document(db.Model):
    """Represents an uploaded document or imported IRM."""

    __tablename__ = "documents"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(Text, nullable=True)  # Extracted markdown or IRM content
    recommendation = db.Column(Text, nullable=True)  # AI recommendation
    metadata_ = db.Column("metadata", JSONB, default=dict)
    source = db.Column(db.String(50), default="upload")  # 'upload' or 'bac'
    irm_id = db.Column(db.String(36), nullable=True)  # Reference to BAC IRM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    sessions = db.relationship("ChatSession", backref="document", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Document {self.id}: {self.filename}>"

    def to_dict(self) -> dict:
        """Serialize document to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "content": self.content,
            "recommendation": self.recommendation,
            "metadata": self.metadata_ or {},
            "source": self.source,
            "irm_id": self.irm_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def create(
        cls,
        filename: str,
        content: Optional[str] = None,
        recommendation: Optional[str] = None,
        metadata: Optional[dict] = None,
        source: str = "upload",
        irm_id: Optional[str] = None,
    ) -> "Document":
        """Create and persist a new document."""
        doc = cls(
            filename=filename,
            content=content,
            recommendation=recommendation,
            metadata_=metadata or {},
            source=source,
            irm_id=irm_id,
        )
        db.session.add(doc)
        db.session.commit()
        return doc

    @classmethod
    def get_by_id(cls, doc_id: str) -> Optional["Document"]:
        """Get document by ID."""
        return cls.query.get(doc_id)

    @classmethod
    def get_all(cls, source: Optional[str] = None, limit: int = 100) -> List["Document"]:
        """Get all documents, optionally filtered by source."""
        query = cls.query
        if source:
            query = query.filter_by(source=source)
        return query.order_by(cls.created_at.desc()).limit(limit).all()
