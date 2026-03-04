"""
BAC - IRM (Intermediate Representation Model) Data Model
JSON-LD compatible SQLAlchemy models for Use Case Descriptions

Based on SACP IRM schema: https://inovia.solutions/sacp/schema#
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.extensions import db


# IRM JSON-LD Context
IRM_CONTEXT = "https://inovia.solutions/sacp/schema#"


class SectionType(str, Enum):
    """Valid section types for Use Case Description."""
    OVERVIEW = "Overview"
    CONTEXT = "BusinessContext"
    OBJECTIVES = "SMARTObjective"
    USER_JOURNEYS = "UserJourney"
    ASSUMPTIONS = "Assumptions"
    OPEN_QUESTIONS = "OpenQuestions"
    BAM_REFERENCES = "BAMReferences"
    VALIDATION = "ValidationStatus"
    CUSTOM = "CustomSection"


class SectionStatus(str, Enum):
    """Validation status for sections."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class IRMState(str, Enum):
    """
    IRM Object Lifecycle States per SACP Architecture Spec.

    Lifecycle flow:
    EXTRACTING → EXTRACTED → PENDING_REVIEW → IN_REVIEW → APPROVED
                                                       ↘ REJECTED
                                            ↗ MODIFIED ↗
    """
    EXTRACTING = "extracting"        # Agent is processing/generating content
    EXTRACTED = "extracted"          # Content created, awaiting review queue
    PENDING_REVIEW = "pending_review"  # Queued for human review
    IN_REVIEW = "in_review"          # Human actively reviewing
    MODIFIED = "modified"            # Changed after review, needs re-review
    APPROVED = "approved"            # Human validated and approved
    REJECTED = "rejected"            # Human rejected


# Valid state transitions - defines the state machine
IRM_STATE_TRANSITIONS = {
    IRMState.EXTRACTING: [IRMState.EXTRACTED, IRMState.REJECTED],
    IRMState.EXTRACTED: [IRMState.PENDING_REVIEW, IRMState.REJECTED],
    IRMState.PENDING_REVIEW: [IRMState.IN_REVIEW, IRMState.REJECTED],
    IRMState.IN_REVIEW: [IRMState.APPROVED, IRMState.REJECTED, IRMState.MODIFIED],
    IRMState.MODIFIED: [IRMState.PENDING_REVIEW, IRMState.IN_REVIEW, IRMState.REJECTED],
    IRMState.APPROVED: [IRMState.MODIFIED],  # Can be modified even after approval
    IRMState.REJECTED: [],  # Terminal state
}


class StateTransition(db.Model):
    """
    Audit log for IRM state transitions.
    Tracks who changed state, when, and why - enables rollback and compliance.
    """
    __tablename__ = "state_transitions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = db.Column(db.String(50), nullable=False)  # 'use_case', 'section'
    entity_id = db.Column(db.String(36), nullable=False, index=True)
    from_state = db.Column(db.String(50), nullable=True)  # null for initial state
    to_state = db.Column(db.String(50), nullable=False)
    triggered_by = db.Column(db.String(100), default="system")  # user_id or 'system'
    reason = db.Column(Text, nullable=True)  # Optional reason for transition
    extra_data = db.Column(JSONB, default=dict)  # Additional context (can't use 'metadata' - reserved)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self) -> dict:
        """Convert to dict for API response."""
        return {
            "id": self.id,
            "entityType": self.entity_type,
            "entityId": self.entity_id,
            "fromState": self.from_state,
            "toState": self.to_state,
            "triggeredBy": self.triggered_by,
            "reason": self.reason,
            "extraData": self.extra_data,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def log_transition(
        cls,
        entity_type: str,
        entity_id: str,
        from_state: Optional[str],
        to_state: str,
        triggered_by: str = "system",
        reason: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> "StateTransition":
        """Record a state transition in the audit log."""
        transition = cls(
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=from_state,
            to_state=to_state,
            triggered_by=triggered_by,
            reason=reason,
            extra_data=extra_data or {},
        )
        db.session.add(transition)
        db.session.commit()
        return transition

    @classmethod
    def get_history(cls, entity_type: str, entity_id: str) -> List["StateTransition"]:
        """Get transition history for an entity."""
        return cls.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(cls.created_at.desc()).all()


class BAMReference(db.Model):
    """Reference to an element in an architecture tool (HOPEX, Signavio)."""
    __tablename__ = "bam_references"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = db.Column(db.String(36), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    tool_type = db.Column(db.String(50), default="HOPEX")  # HOPEX, Signavio
    element_id = db.Column(db.String(255), default="")
    element_type = db.Column(db.String(100), default="")  # BusinessCapability, BusinessProcess, etc.
    element_name = db.Column(db.String(255), default="")
    diagram_id = db.Column(db.String(255), nullable=True)
    embed_url = db.Column(Text, nullable=True)
    embed_image_base64 = db.Column(Text, nullable=True)
    deep_link = db.Column(Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to IRM JSON-LD format."""
        return {
            "@type": "sacp:BAMReference",
            "@id": f"urn:bam-ref:{self.id}",
            "sacp:toolType": self.tool_type,
            "sacp:elementId": self.element_id,
            "sacp:elementType": self.element_type,
            "sacp:elementName": self.element_name,
            "sacp:diagramId": self.diagram_id,
            "sacp:embedUrl": self.embed_url,
            "sacp:deepLink": self.deep_link,
        }

    @classmethod
    def create(cls, section_id: str, **kwargs) -> "BAMReference":
        """Create and persist a new BAM reference."""
        ref = cls(section_id=section_id, **kwargs)
        db.session.add(ref)
        db.session.commit()
        return ref


class Section(db.Model):
    """A section within a Use Case Description."""
    __tablename__ = "sections"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    use_case_id = db.Column(db.String(36), ForeignKey("use_cases.id", ondelete="CASCADE"), nullable=False)
    section_type = db.Column(db.String(50), default=SectionType.OVERVIEW.value)
    title = db.Column(db.String(255), default="")
    content = db.Column(Text, default="")  # Markdown content
    order = db.Column(db.Integer, default=0)

    # Metadata as JSONB (replaces IRMMeta dataclass)
    meta = db.Column(JSONB, default=lambda: {
        "created_by": "bac-system",
        "created_at": datetime.utcnow().isoformat(),
        "version": "0.1",
        "source_document": None,
        "source_section": None,
        "status": SectionStatus.DRAFT.value,
        "confidence": None,
        "last_validated_by": None,
        "last_validated_at": None,
    })

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bam_references = relationship("BAMReference", backref="section", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to IRM JSON-LD format."""
        section_type_value = self.section_type
        if isinstance(section_type_value, SectionType):
            section_type_value = section_type_value.value

        # Format meta for JSON-LD
        meta_dict = self.meta or {}
        json_ld_meta = {
            "sacp:createdBy": meta_dict.get("created_by", "bac-system"),
            "sacp:createdAt": meta_dict.get("created_at"),
            "sacp:version": meta_dict.get("version", "0.1"),
            "sacp:sourceDocument": meta_dict.get("source_document"),
            "sacp:sourceSection": meta_dict.get("source_section"),
            "sacp:validationStatus": meta_dict.get("status", SectionStatus.DRAFT.value),
            "sacp:confidence": meta_dict.get("confidence"),
            "sacp:lastValidatedBy": meta_dict.get("last_validated_by"),
            "sacp:lastValidatedAt": meta_dict.get("last_validated_at"),
        }

        return {
            "@type": f"sacp:{section_type_value}",
            "@id": f"urn:section:{self.id}",
            "sacp:title": self.title,
            "sacp:content": self.content,
            "sacp:order": self.order,
            "sacp:bamReferences": [ref.to_dict() for ref in self.bam_references],
            "sacp:meta": json_ld_meta,
        }

    def to_summary_dict(self) -> dict:
        """Return a simpler dict for list views."""
        meta_dict = self.meta or {}
        return {
            "id": self.id,
            "type": self.section_type,
            "title": self.title,
            "order": self.order,
            "status": meta_dict.get("status", SectionStatus.DRAFT.value),
            "bamReferenceCount": self.bam_references.count(),
        }

    def add_bam_reference(self, **kwargs) -> BAMReference:
        """Add a BAM reference to this section."""
        ref = BAMReference(section_id=self.id, **kwargs)
        db.session.add(ref)
        db.session.commit()
        return ref

    def remove_bam_reference(self, ref_id: str) -> bool:
        """Remove a BAM reference by ID."""
        ref = BAMReference.query.filter_by(id=ref_id, section_id=self.id).first()
        if ref:
            db.session.delete(ref)
            db.session.commit()
            return True
        return False


class UseCase(db.Model):
    """
    The primary output of BAC - a Business Use Case Description.
    Stored as IRM JSON-LD.
    """
    __tablename__ = "use_cases"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), default="New Use Case")
    description = db.Column(Text, default="")
    template_id = db.Column(db.String(100), nullable=True)

    # IRM Lifecycle State
    state = db.Column(db.String(50), default=IRMState.EXTRACTING.value, index=True)

    # Metadata as JSONB (replaces IRMMeta dataclass)
    meta = db.Column(JSONB, default=lambda: {
        "created_by": "bac-system",
        "created_at": datetime.utcnow().isoformat(),
        "version": "0.1",
        "source_document": None,
        "source_section": None,
        "status": SectionStatus.DRAFT.value,
        "confidence": None,
        "last_validated_by": None,
        "last_validated_at": None,
    })

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sections = relationship("Section", backref="use_case", lazy="dynamic", cascade="all, delete-orphan",
                           order_by="Section.order")

    def __repr__(self) -> str:
        return f"<UseCase {self.id}: {self.title}>"

    def to_dict(self) -> dict:
        """Convert to IRM JSON-LD format for export."""
        # Format meta for JSON-LD
        meta_dict = self.meta or {}
        json_ld_meta = {
            "sacp:createdBy": meta_dict.get("created_by", "bac-system"),
            "sacp:createdAt": meta_dict.get("created_at"),
            "sacp:version": meta_dict.get("version", "0.1"),
            "sacp:sourceDocument": meta_dict.get("source_document"),
            "sacp:sourceSection": meta_dict.get("source_section"),
            "sacp:validationStatus": meta_dict.get("status", SectionStatus.DRAFT.value),
            "sacp:confidence": meta_dict.get("confidence"),
            "sacp:lastValidatedBy": meta_dict.get("last_validated_by"),
            "sacp:lastValidatedAt": meta_dict.get("last_validated_at"),
        }

        return {
            "@context": IRM_CONTEXT,
            "@type": "sacp:UseCaseDescription",
            "@id": f"urn:usecase:{self.id}",
            "sacp:title": self.title,
            "sacp:description": self.description,
            "sacp:templateId": self.template_id,
            "sacp:sections": [s.to_dict() for s in self.sections.order_by(Section.order)],
            "sacp:meta": json_ld_meta,
        }

    def to_summary_dict(self) -> dict:
        """Return a simpler dict for list views."""
        meta_dict = self.meta or {}
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description[:200] if self.description else "",
            "templateId": self.template_id,
            "sectionCount": self.sections.count(),
            "status": meta_dict.get("status", SectionStatus.DRAFT.value),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def add_section(self, section_type: str = "Overview", title: str = "", content: str = "") -> Section:
        """Add a new section to the use case."""
        # Determine order
        max_order = db.session.query(db.func.max(Section.order)).filter(
            Section.use_case_id == self.id
        ).scalar() or -1

        # Convert string to enum value if needed
        try:
            section_type_value = SectionType(section_type).value
        except ValueError:
            section_type_value = SectionType.CUSTOM.value

        meta_dict = self.meta or {}
        section = Section(
            use_case_id=self.id,
            section_type=section_type_value,
            title=title,
            content=content,
            order=max_order + 1,
            meta={
                "created_by": meta_dict.get("created_by", "bac-system"),
                "created_at": datetime.utcnow().isoformat(),
                "version": "0.1",
                "source_document": meta_dict.get("source_document"),
                "source_section": None,
                "status": SectionStatus.DRAFT.value,
                "confidence": None,
                "last_validated_by": None,
                "last_validated_at": None,
            }
        )
        db.session.add(section)
        db.session.commit()
        return section

    def get_section(self, section_id: str) -> Optional[Section]:
        """Get a section by ID."""
        return Section.query.filter_by(id=section_id, use_case_id=self.id).first()

    def update_section(self, section_id: str, data: dict) -> Optional[Section]:
        """Update a section by ID."""
        section = self.get_section(section_id)
        if not section:
            return None

        if "title" in data:
            section.title = data["title"]
        if "content" in data:
            section.content = data["content"]
        if "order" in data:
            section.order = data["order"]
        if "type" in data:
            try:
                section.section_type = SectionType(data["type"]).value
            except ValueError:
                section.section_type = SectionType.CUSTOM.value

        db.session.commit()
        return section

    def delete_section(self, section_id: str) -> bool:
        """Delete a section by ID."""
        section = self.get_section(section_id)
        if section:
            db.session.delete(section)
            db.session.commit()
            return True
        return False

    def reorder_sections(self, section_ids: List[str]) -> None:
        """Reorder sections based on provided ID list."""
        for i, sid in enumerate(section_ids):
            section = self.get_section(sid)
            if section:
                section.order = i
        db.session.commit()

    def is_ready_for_export(self) -> bool:
        """Check if use case is ready for export."""
        # Must have at least one section with content
        return self.sections.filter(Section.content != "").count() > 0

    def get_export_warnings(self) -> List[str]:
        """Get warnings about potential export issues."""
        warnings = []

        if self.sections.count() == 0:
            warnings.append("No sections defined")
        elif self.sections.filter(Section.content != "").count() == 0:
            warnings.append("All sections are empty")

        # Check for broken BAM references
        for section in self.sections:
            for ref in section.bam_references:
                if not ref.element_id:
                    warnings.append(f"Section '{section.title}' has invalid BAM reference")

        return warnings

    # ============================================
    # IRM State Machine Methods
    # ============================================

    def get_state(self) -> IRMState:
        """Get current state as enum."""
        try:
            return IRMState(self.state)
        except ValueError:
            return IRMState.EXTRACTING

    def can_transition_to(self, new_state: IRMState) -> bool:
        """Check if transition to new_state is valid."""
        current = self.get_state()
        valid_transitions = IRM_STATE_TRANSITIONS.get(current, [])
        return new_state in valid_transitions

    def get_valid_transitions(self) -> List[IRMState]:
        """Get list of valid next states from current state."""
        return IRM_STATE_TRANSITIONS.get(self.get_state(), [])

    def transition_to(
        self,
        new_state: IRMState,
        triggered_by: str = "system",
        reason: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """
        Transition to a new state with validation and audit logging.

        Args:
            new_state: Target state
            triggered_by: User ID or 'system'
            reason: Optional reason for the transition
            force: If True, bypass transition validation (use with caution)

        Returns:
            True if transition succeeded, False otherwise
        """
        current = self.get_state()

        # Validate transition
        if not force and not self.can_transition_to(new_state):
            return False

        # Log the transition
        StateTransition.log_transition(
            entity_type="use_case",
            entity_id=self.id,
            from_state=current.value,
            to_state=new_state.value,
            triggered_by=triggered_by,
            reason=reason,
            extra_data={"title": self.title},
        )

        # Update state
        self.state = new_state.value
        db.session.commit()
        return True

    def get_state_history(self) -> List[dict]:
        """Get full state transition history."""
        transitions = StateTransition.get_history("use_case", self.id)
        return [t.to_dict() for t in transitions]

    def submit_for_review(self, triggered_by: str = "system") -> bool:
        """Convenience method: Move from EXTRACTED to PENDING_REVIEW."""
        current = self.get_state()
        if current == IRMState.EXTRACTED:
            return self.transition_to(IRMState.PENDING_REVIEW, triggered_by, "Submitted for review")
        elif current == IRMState.MODIFIED:
            return self.transition_to(IRMState.PENDING_REVIEW, triggered_by, "Re-submitted for review after modification")
        return False

    def start_review(self, reviewer_id: str) -> bool:
        """Convenience method: Move from PENDING_REVIEW to IN_REVIEW."""
        if self.get_state() == IRMState.PENDING_REVIEW:
            return self.transition_to(IRMState.IN_REVIEW, reviewer_id, f"Review started by {reviewer_id}")
        return False

    def approve(self, reviewer_id: str, reason: Optional[str] = None) -> bool:
        """Convenience method: Approve the use case."""
        if self.get_state() == IRMState.IN_REVIEW:
            return self.transition_to(IRMState.APPROVED, reviewer_id, reason or "Approved")
        return False

    def reject(self, reviewer_id: str, reason: str) -> bool:
        """Convenience method: Reject the use case."""
        current = self.get_state()
        if current in [IRMState.EXTRACTING, IRMState.EXTRACTED, IRMState.PENDING_REVIEW, IRMState.IN_REVIEW, IRMState.MODIFIED]:
            return self.transition_to(IRMState.REJECTED, reviewer_id, reason)
        return False

    def mark_modified(self, modifier_id: str, reason: Optional[str] = None) -> bool:
        """Convenience method: Mark as modified (needs re-review)."""
        current = self.get_state()
        if current in [IRMState.IN_REVIEW, IRMState.APPROVED]:
            return self.transition_to(IRMState.MODIFIED, modifier_id, reason or "Content modified")
        return False

    def complete_extraction(self, triggered_by: str = "system") -> bool:
        """Convenience method: Mark extraction as complete."""
        if self.get_state() == IRMState.EXTRACTING:
            return self.transition_to(IRMState.EXTRACTED, triggered_by, "Extraction completed")
        return False

    # ============================================
    # Class methods for CRUD operations
    # ============================================

    @classmethod
    def create(
        cls,
        title: str = "New Use Case",
        description: str = "",
        template_id: Optional[str] = None,
        created_by: str = "bac-system",
    ) -> "UseCase":
        """Create and persist a new use case."""
        use_case = cls(
            title=title,
            description=description,
            template_id=template_id,
            meta={
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat(),
                "version": "0.1",
                "source_document": None,
                "source_section": None,
                "status": SectionStatus.DRAFT.value,
                "confidence": None,
                "last_validated_by": None,
                "last_validated_at": None,
            }
        )
        db.session.add(use_case)
        db.session.commit()

        # Apply template if specified
        if template_id:
            try:
                from app.utilities.templates import apply_template
                apply_template(use_case, template_id)
            except ImportError:
                pass  # Template utilities may not be available

        return use_case

    @classmethod
    def get_by_id(cls, use_case_id: str) -> Optional["UseCase"]:
        """Get a use case by ID."""
        return cls.query.get(use_case_id)

    @classmethod
    def get_all(cls, limit: int = 100) -> List["UseCase"]:
        """Get all use cases."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def update(cls, use_case_id: str, data: dict) -> Optional["UseCase"]:
        """Update a use case by ID."""
        use_case = cls.get_by_id(use_case_id)
        if not use_case:
            return None

        if "title" in data:
            use_case.title = data["title"]
        if "description" in data:
            use_case.description = data["description"]

        db.session.commit()
        return use_case

    @classmethod
    def delete(cls, use_case_id: str) -> bool:
        """Delete a use case by ID."""
        use_case = cls.get_by_id(use_case_id)
        if use_case:
            db.session.delete(use_case)
            db.session.commit()
            return True
        return False


# ============================================
# Compatibility layer for existing code
# These functions delegate to the UseCase class methods
# ============================================

def create_use_case(session_id: str = None, title: str = "New Use Case", template_id: str = None) -> UseCase:
    """Create a new use case, optionally from a template."""
    created_by = f"session:{session_id}" if session_id else "bac-system"
    return UseCase.create(title=title, template_id=template_id, created_by=created_by)


def get_use_case(use_case_id: str) -> Optional[UseCase]:
    """Get a use case by ID."""
    return UseCase.get_by_id(use_case_id)


def update_use_case(use_case_id: str, data: dict) -> Optional[UseCase]:
    """Update a use case by ID."""
    return UseCase.update(use_case_id, data)


def delete_use_case(use_case_id: str) -> bool:
    """Delete a use case by ID."""
    return UseCase.delete(use_case_id)


def list_use_cases(session_id: str = None) -> List[dict]:
    """List all use cases."""
    use_cases = UseCase.get_all()
    return [uc.to_summary_dict() for uc in use_cases]
