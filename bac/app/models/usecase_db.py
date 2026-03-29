"""
BAC - Database-backed Use Case Storage
SQLAlchemy models for persisting use cases to PostgreSQL
"""
from datetime import datetime
from typing import Optional, List
import json
import uuid

from app.extensions import db
from app.models.irm import IRMState, IRM_STATE_TRANSITIONS, StateTransition


class UseCaseModel(db.Model):
    """SQLAlchemy model for persisting use cases."""
    __tablename__ = "bac_use_cases"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False, default="New Use Case")
    description = db.Column(db.Text, default="")
    template_id = db.Column(db.String(100), nullable=True)
    sections_json = db.Column(db.Text, default="[]")  # JSON array of sections
    meta_json = db.Column(db.Text, default="{}")  # JSON object for metadata
    state = db.Column(db.String(50), default=IRMState.EXTRACTING.value, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to IRM JSON-LD format."""
        sections = json.loads(self.sections_json) if self.sections_json else []
        meta = json.loads(self.meta_json) if self.meta_json else {}

        return {
            "@context": "https://inovia.solutions/sacp/schema#",
            "@type": "sacp:UseCaseDescription",
            "@id": f"urn:usecase:{self.id}",
            "sacp:title": self.title,
            "sacp:description": self.description or "",
            "sacp:templateId": self.template_id,
            "sacp:sections": sections,
            "sacp:meta": {
                "sacp:createdBy": meta.get("created_by", "bac-system"),
                "sacp:createdAt": self.created_at.isoformat() if self.created_at else None,
                "sacp:version": meta.get("version", "0.1"),
                "sacp:validationStatus": meta.get("status", "draft"),
                "sacp:confidence": meta.get("confidence"),
                "sacp:sourceDocument": meta.get("source_document"),
                "sacp:sourceSection": meta.get("source_section"),
                "sacp:lastValidatedBy": meta.get("last_validated_by"),
                "sacp:lastValidatedAt": meta.get("last_validated_at"),
            },
        }

    def to_list_item(self) -> dict:
        """Convert to list view summary."""
        sections = json.loads(self.sections_json) if self.sections_json else []
        meta = json.loads(self.meta_json) if self.meta_json else {}

        return {
            "id": self.id,
            "title": self.title,
            "sectionCount": len(sections),
            "status": meta.get("status", "draft"),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def get_sections(self) -> list:
        """Get sections as list of dicts."""
        return json.loads(self.sections_json) if self.sections_json else []

    def set_sections(self, sections: list) -> None:
        """Set sections from list of dicts."""
        self.sections_json = json.dumps(sections)

    def add_section(self, section_type: str, title: str, content: str = "") -> dict:
        """Add a new section."""
        sections = self.get_sections()
        max_order = max((s.get("order", 0) for s in sections), default=-1)

        new_section = {
            "@type": f"sacp:{section_type}",
            "@id": f"urn:section:{uuid.uuid4()}",
            "id": str(uuid.uuid4()),
            "sacp:title": title,
            "sacp:content": content,
            "sacp:order": max_order + 1,
            "sacp:bamReferences": [],
            "sacp:meta": {
                "sacp:createdBy": "bac-system",
                "sacp:createdAt": datetime.utcnow().isoformat(),
                "sacp:validationStatus": "draft",
            }
        }

        sections.append(new_section)
        self.set_sections(sections)
        return new_section

    def update_section(self, section_id: str, data: dict) -> Optional[dict]:
        """Update a section by ID."""
        sections = self.get_sections()

        for i, section in enumerate(sections):
            if section.get("id") == section_id or section.get("@id") == f"urn:section:{section_id}":
                if "title" in data:
                    section["sacp:title"] = data["title"]
                if "content" in data:
                    section["sacp:content"] = data["content"]
                if "order" in data:
                    section["sacp:order"] = data["order"]
                sections[i] = section
                self.set_sections(sections)
                return section

        return None

    def delete_section(self, section_id: str) -> bool:
        """Delete a section by ID."""
        sections = self.get_sections()

        for i, section in enumerate(sections):
            if section.get("id") == section_id or section.get("@id") == f"urn:section:{section_id}":
                sections.pop(i)
                self.set_sections(sections)
                return True

        return False

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
        """Transition to a new state with validation and audit logging."""
        current = self.get_state()

        if not force and not self.can_transition_to(new_state):
            return False

        StateTransition.log_transition(
            entity_type="use_case",
            entity_id=self.id,
            from_state=current.value,
            to_state=new_state.value,
            triggered_by=triggered_by,
            reason=reason,
            extra_data={"title": self.title},
        )

        self.state = new_state.value
        db.session.commit()
        return True

    def get_state_history(self) -> List[dict]:
        """Get full state transition history."""
        transitions = StateTransition.get_history("use_case", self.id)
        return [t.to_dict() for t in transitions]

    def complete_extraction(self, triggered_by: str = "system") -> bool:
        """Mark extraction as complete (EXTRACTING -> EXTRACTED)."""
        if self.get_state() == IRMState.EXTRACTING:
            return self.transition_to(IRMState.EXTRACTED, triggered_by, "Extraction completed")
        return False

    def submit_for_review(self, triggered_by: str = "system") -> bool:
        """Submit for HITL review (EXTRACTED/MODIFIED -> PENDING_REVIEW)."""
        current = self.get_state()
        if current == IRMState.EXTRACTED:
            return self.transition_to(IRMState.PENDING_REVIEW, triggered_by, "Submitted for review")
        elif current == IRMState.MODIFIED:
            return self.transition_to(IRMState.PENDING_REVIEW, triggered_by, "Re-submitted after modification")
        return False

    def start_review(self, reviewer_id: str) -> bool:
        """Start HITL review (PENDING_REVIEW -> IN_REVIEW)."""
        if self.get_state() == IRMState.PENDING_REVIEW:
            return self.transition_to(IRMState.IN_REVIEW, reviewer_id, f"Review started by {reviewer_id}")
        return False

    def approve(self, reviewer_id: str, reason: Optional[str] = None) -> bool:
        """Approve the use case (IN_REVIEW -> APPROVED)."""
        if self.get_state() == IRMState.IN_REVIEW:
            return self.transition_to(IRMState.APPROVED, reviewer_id, reason or "Approved")
        return False

    def reject(self, reviewer_id: str, reason: str) -> bool:
        """Reject the use case (various states -> REJECTED)."""
        current = self.get_state()
        if current in [IRMState.EXTRACTING, IRMState.EXTRACTED, IRMState.PENDING_REVIEW, IRMState.IN_REVIEW, IRMState.MODIFIED]:
            return self.transition_to(IRMState.REJECTED, reviewer_id, reason)
        return False

    def mark_modified(self, modifier_id: str, reason: Optional[str] = None) -> bool:
        """Mark as modified (IN_REVIEW/APPROVED -> MODIFIED)."""
        current = self.get_state()
        if current in [IRMState.IN_REVIEW, IRMState.APPROVED]:
            return self.transition_to(IRMState.MODIFIED, modifier_id, reason or "Content modified")
        return False


# Database-backed CRUD functions
def create_use_case_db(session_id: str = None, title: str = "New Use Case", template_id: str = None) -> UseCaseModel:
    """Create a new use case in the database."""
    meta = {
        "created_by": f"session:{session_id}" if session_id else "bac-system",
        "status": "draft",
        "version": "0.1",
    }

    use_case = UseCaseModel(
        title=title,
        template_id=template_id,
        meta_json=json.dumps(meta),
    )

    # Apply template if specified
    if template_id:
        _apply_template_to_model(use_case, template_id)

    db.session.add(use_case)
    db.session.commit()

    return use_case


def get_use_case_db(use_case_id: str) -> Optional[UseCaseModel]:
    """Get a use case by ID."""
    return UseCaseModel.query.get(use_case_id)


def update_use_case_db(use_case_id: str, data: dict) -> Optional[UseCaseModel]:
    """Update a use case by ID."""
    use_case = UseCaseModel.query.get(use_case_id)
    if not use_case:
        return None

    if "title" in data:
        use_case.title = data["title"]
    if "description" in data:
        use_case.description = data["description"]

    db.session.commit()
    return use_case


def delete_use_case_db(use_case_id: str) -> bool:
    """Delete a use case by ID."""
    use_case = UseCaseModel.query.get(use_case_id)
    if not use_case:
        return False

    db.session.delete(use_case)
    db.session.commit()
    return True


def list_use_cases_db(session_id: str = None) -> list[dict]:
    """List all use cases."""
    use_cases = UseCaseModel.query.order_by(UseCaseModel.created_at.desc()).all()
    return [uc.to_list_item() for uc in use_cases]


def _apply_template_to_model(use_case: UseCaseModel, template_id: str) -> None:
    """Apply a template to a use case model."""
    templates = {
        "Regulatory Change": [
            {"type": "Overview", "title": "Regulatory Overview", "content": ""},
            {"type": "BusinessContext", "title": "Business Impact", "content": ""},
            {"type": "SMARTObjective", "title": "Compliance Objectives", "content": ""},
            {"type": "UserJourney", "title": "Affected Processes", "content": ""},
            {"type": "Assumptions", "title": "Assumptions & Constraints", "content": ""},
        ],
        "Digital Transformation": [
            {"type": "Overview", "title": "Transformation Overview", "content": ""},
            {"type": "BusinessContext", "title": "Current State", "content": ""},
            {"type": "SMARTObjective", "title": "Target State Objectives", "content": ""},
            {"type": "UserJourney", "title": "User Journeys", "content": ""},
            {"type": "Assumptions", "title": "Technical Assumptions", "content": ""},
        ],
        "Process Improvement": [
            {"type": "Overview", "title": "Process Overview", "content": ""},
            {"type": "BusinessContext", "title": "Current Process", "content": ""},
            {"type": "SMARTObjective", "title": "Improvement Goals", "content": ""},
            {"type": "UserJourney", "title": "New Process Flow", "content": ""},
            {"type": "OpenQuestions", "title": "Open Questions", "content": ""},
        ],
    }

    template_sections = templates.get(template_id, [])
    for section_data in template_sections:
        use_case.add_section(
            section_type=section_data["type"],
            title=section_data["title"],
            content=section_data["content"],
        )
