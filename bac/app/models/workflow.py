"""
BAC - Workflow Step Framework
Implements the 5-step workflow per SACP Architecture Spec:
  1. Ingest Requirements
  2. Find Use Case Blueprint (Catena-X)
  3. Incorporate Reference Architecture (Tractus-X)
  4. Incorporate Digital Landscape
  5. Export to HOPEX

Each step stores intermediate results enabling rollback and audit.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class WorkflowStepType(str, Enum):
    """The 5 workflow steps per SACP architecture."""
    REQUIREMENTS = "requirements"       # Step 1: Ingest requirements document
    BLUEPRINT = "blueprint"             # Step 2: Match to Catena-X use case blueprint
    REFERENCE_ARCH = "reference_arch"   # Step 3: Incorporate Tractus-X reference architecture
    LANDSCAPE = "landscape"             # Step 4: Incorporate digital landscape (HOPEX read)
    EXPORT = "export"                   # Step 5: Export to HOPEX


class WorkflowStepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "pending"           # Not started
    IN_PROGRESS = "in_progress"   # Currently executing
    AWAITING_REVIEW = "awaiting_review"  # Needs human approval
    COMPLETED = "completed"       # Successfully finished
    FAILED = "failed"             # Execution failed
    SKIPPED = "skipped"           # User chose to skip
    ROLLED_BACK = "rolled_back"   # Reverted to previous state


# Step ordering and dependencies
WORKFLOW_STEP_ORDER = [
    WorkflowStepType.REQUIREMENTS,
    WorkflowStepType.BLUEPRINT,
    WorkflowStepType.REFERENCE_ARCH,
    WorkflowStepType.LANDSCAPE,
    WorkflowStepType.EXPORT,
]

# Which steps require HITL approval before proceeding
HITL_REQUIRED_STEPS = {
    WorkflowStepType.REQUIREMENTS,   # Review extracted requirements
    WorkflowStepType.BLUEPRINT,      # Confirm blueprint selection
    WorkflowStepType.REFERENCE_ARCH, # Review architecture mapping
}


class WorkflowStep(db.Model):
    """
    A single step in the use case generation workflow.
    Stores input, output, and status for each step.
    """
    __tablename__ = "workflow_steps"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    use_case_id = db.Column(db.String(36), db.ForeignKey("bac_use_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = db.Column(db.Integer, nullable=False)  # 1-5
    step_type = db.Column(db.String(50), nullable=False)  # WorkflowStepType value
    status = db.Column(db.String(50), default=WorkflowStepStatus.PENDING.value)

    # Input/Output data as JSON
    input_data = db.Column(JSONB, default=dict)   # What was fed into this step
    output_data = db.Column(JSONB, default=dict)  # What the step produced
    error_data = db.Column(JSONB, default=dict)   # Error details if failed

    # Execution metadata
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    executed_by = db.Column(db.String(100), default="system")  # user_id or 'system'/'agent'

    # HITL review tracking
    requires_review = db.Column(db.Boolean, default=False)
    reviewed_by = db.Column(db.String(100), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dict for API response."""
        return {
            "id": self.id,
            "useCaseId": self.use_case_id,
            "stepNumber": self.step_number,
            "stepType": self.step_type,
            "status": self.status,
            "inputData": self.input_data,
            "outputData": self.output_data,
            "errorData": self.error_data,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "executedBy": self.executed_by,
            "requiresReview": self.requires_review,
            "reviewedBy": self.reviewed_by,
            "reviewedAt": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewNotes": self.review_notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def to_summary_dict(self) -> dict:
        """Minimal summary for list views."""
        return {
            "id": self.id,
            "stepNumber": self.step_number,
            "stepType": self.step_type,
            "status": self.status,
            "requiresReview": self.requires_review,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
        }

    def start(self, executed_by: str = "system") -> None:
        """Mark step as started."""
        self.status = WorkflowStepStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow()
        self.executed_by = executed_by
        db.session.commit()

    def complete(self, output_data: dict, requires_review: bool = None) -> None:
        """Mark step as completed with output data."""
        self.status = WorkflowStepStatus.COMPLETED.value
        self.output_data = output_data
        self.completed_at = datetime.utcnow()

        # Set review requirement based on step type if not explicitly specified
        if requires_review is None:
            step_type = WorkflowStepType(self.step_type)
            self.requires_review = step_type in HITL_REQUIRED_STEPS
        else:
            self.requires_review = requires_review

        if self.requires_review:
            self.status = WorkflowStepStatus.AWAITING_REVIEW.value

        db.session.commit()

    def fail(self, error_data: dict) -> None:
        """Mark step as failed with error details."""
        self.status = WorkflowStepStatus.FAILED.value
        self.error_data = error_data
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def skip(self, reason: str = None) -> None:
        """Mark step as skipped."""
        self.status = WorkflowStepStatus.SKIPPED.value
        self.completed_at = datetime.utcnow()
        if reason:
            self.error_data = {"skip_reason": reason}
        db.session.commit()

    def approve_review(self, reviewer_id: str, notes: str = None) -> None:
        """Approve this step after HITL review."""
        self.status = WorkflowStepStatus.COMPLETED.value
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        self.requires_review = False
        db.session.commit()

    def reject_review(self, reviewer_id: str, notes: str) -> None:
        """Reject this step, requiring re-execution."""
        self.status = WorkflowStepStatus.FAILED.value
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        self.requires_review = False
        db.session.commit()

    def rollback(self) -> None:
        """Roll back this step, clearing output."""
        self.status = WorkflowStepStatus.ROLLED_BACK.value
        self.output_data = {}
        self.error_data = {"rolled_back_at": datetime.utcnow().isoformat()}
        self.completed_at = None
        self.reviewed_by = None
        self.reviewed_at = None
        self.review_notes = None
        db.session.commit()


class Workflow(db.Model):
    """
    Represents the overall workflow for a use case.
    Tracks current step and provides workflow-level operations.
    """
    __tablename__ = "workflows"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    use_case_id = db.Column(db.String(36), db.ForeignKey("bac_use_cases.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    current_step = db.Column(db.Integer, default=0)  # 0 = not started, 1-5 = step number
    status = db.Column(db.String(50), default="not_started")  # not_started, in_progress, completed, failed

    # Timestamps
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to steps
    steps = db.relationship("WorkflowStep", backref="workflow",
                           foreign_keys="WorkflowStep.use_case_id",
                           primaryjoin="Workflow.use_case_id == WorkflowStep.use_case_id",
                           lazy="dynamic", viewonly=True)

    def to_dict(self) -> dict:
        """Convert to dict for API response."""
        return {
            "id": self.id,
            "useCaseId": self.use_case_id,
            "currentStep": self.current_step,
            "status": self.status,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [s.to_summary_dict() for s in self.get_steps()],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def get_steps(self) -> List[WorkflowStep]:
        """Get all steps ordered by step number."""
        return WorkflowStep.query.filter_by(
            use_case_id=self.use_case_id
        ).order_by(WorkflowStep.step_number).all()

    def get_step(self, step_number: int) -> Optional[WorkflowStep]:
        """Get a specific step by number."""
        return WorkflowStep.query.filter_by(
            use_case_id=self.use_case_id,
            step_number=step_number
        ).first()

    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the current active step."""
        if self.current_step == 0:
            return None
        return self.get_step(self.current_step)

    def initialize_steps(self) -> List[WorkflowStep]:
        """Create all 5 workflow steps for this workflow."""
        steps = []
        for i, step_type in enumerate(WORKFLOW_STEP_ORDER, start=1):
            step = WorkflowStep(
                use_case_id=self.use_case_id,
                step_number=i,
                step_type=step_type.value,
                requires_review=step_type in HITL_REQUIRED_STEPS,
            )
            db.session.add(step)
            steps.append(step)
        db.session.commit()
        return steps

    def can_advance(self) -> bool:
        """Check if workflow can advance to next step."""
        if self.status == "completed":
            return False

        current = self.get_current_step()
        if current is None:
            return True  # Can start

        # Current step must be completed (not awaiting review)
        return current.status == WorkflowStepStatus.COMPLETED.value

    def advance(self) -> Optional[WorkflowStep]:
        """Advance to the next step if possible."""
        if not self.can_advance():
            return None

        # Start workflow if not started
        if self.status == "not_started":
            self.status = "in_progress"
            self.started_at = datetime.utcnow()
            self.current_step = 1
        else:
            self.current_step += 1

        # Check if workflow is complete
        if self.current_step > len(WORKFLOW_STEP_ORDER):
            self.status = "completed"
            self.completed_at = datetime.utcnow()
            db.session.commit()
            return None

        db.session.commit()
        return self.get_current_step()

    def rollback_to_step(self, step_number: int) -> bool:
        """
        Roll back workflow to a specific step.
        All subsequent steps will be rolled back.
        """
        if step_number < 1 or step_number > len(WORKFLOW_STEP_ORDER):
            return False

        # Roll back all steps after the target
        for step in self.get_steps():
            if step.step_number >= step_number:
                step.rollback()

        self.current_step = step_number
        self.status = "in_progress"
        self.completed_at = None
        db.session.commit()
        return True

    def get_progress(self) -> dict:
        """Get workflow progress summary."""
        steps = self.get_steps()
        completed = sum(1 for s in steps if s.status == WorkflowStepStatus.COMPLETED.value)
        awaiting_review = sum(1 for s in steps if s.status == WorkflowStepStatus.AWAITING_REVIEW.value)

        return {
            "totalSteps": len(WORKFLOW_STEP_ORDER),
            "completedSteps": completed,
            "awaitingReview": awaiting_review,
            "currentStep": self.current_step,
            "percentComplete": int((completed / len(WORKFLOW_STEP_ORDER)) * 100),
            "status": self.status,
        }

    @classmethod
    def create_for_use_case(cls, use_case_id: str) -> "Workflow":
        """Create a new workflow for a use case with all steps initialized."""
        workflow = cls(use_case_id=use_case_id)
        db.session.add(workflow)
        db.session.commit()

        workflow.initialize_steps()
        return workflow

    @classmethod
    def get_by_use_case(cls, use_case_id: str) -> Optional["Workflow"]:
        """Get workflow for a use case."""
        return cls.query.filter_by(use_case_id=use_case_id).first()

    @classmethod
    def get_or_create(cls, use_case_id: str) -> "Workflow":
        """Get existing workflow or create new one."""
        workflow = cls.get_by_use_case(use_case_id)
        if not workflow:
            workflow = cls.create_for_use_case(use_case_id)
        return workflow
