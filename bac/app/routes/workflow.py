"""
BAC - Workflow API Routes
Manages the 5-step use case generation workflow.
"""
from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.workflow import (
    Workflow,
    WorkflowStep,
    WorkflowStepStatus,
    WORKFLOW_STEP_ORDER,
)
from app.models.usecase_db import UseCaseModel, get_use_case_db

workflow_bp = Blueprint("workflow", __name__)


@workflow_bp.route("/<use_case_id>/workflow", methods=["GET"])
def get_workflow(use_case_id: str):
    """Get workflow status for a use case."""
    # Verify use case exists
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found", "hint": "POST to create one"}), 404

    return jsonify({
        "workflow": workflow.to_dict(),
        "progress": workflow.get_progress(),
    })


@workflow_bp.route("/<use_case_id>/workflow", methods=["POST"])
def create_workflow(use_case_id: str):
    """Create or reset workflow for a use case."""
    # Verify use case exists
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    # Check if workflow already exists
    existing = Workflow.get_by_use_case(use_case_id)
    if existing:
        data = request.json or {}
        if not data.get("reset"):
            return jsonify({
                "error": "Workflow already exists",
                "hint": "Pass {\"reset\": true} to reset workflow"
            }), 409

        # Delete existing workflow and steps
        WorkflowStep.query.filter_by(use_case_id=use_case_id).delete()
        db.session.delete(existing)
        db.session.commit()

    # Create new workflow
    workflow = Workflow.create_for_use_case(use_case_id)

    return jsonify({
        "workflow": workflow.to_dict(),
        "progress": workflow.get_progress(),
    }), 201


@workflow_bp.route("/<use_case_id>/workflow/steps", methods=["GET"])
def list_steps(use_case_id: str):
    """List all workflow steps for a use case."""
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    steps = workflow.get_steps()
    return jsonify({
        "steps": [s.to_dict() for s in steps],
        "currentStep": workflow.current_step,
    })


@workflow_bp.route("/<use_case_id>/workflow/steps/<int:step_number>", methods=["GET"])
def get_step(use_case_id: str, step_number: int):
    """Get a specific workflow step."""
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    step = workflow.get_step(step_number)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    return jsonify(step.to_dict())


@workflow_bp.route("/<use_case_id>/workflow/steps/<int:step_number>/execute", methods=["POST"])
def execute_step(use_case_id: str, step_number: int):
    """
    Execute a workflow step.

    Body can include:
    - input_data: dict of input data for the step
    - executed_by: user/agent ID
    """
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    step = workflow.get_step(step_number)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    # Verify this is the current step or workflow allows it
    if workflow.current_step != step_number and workflow.current_step != 0:
        return jsonify({
            "error": "Cannot execute this step",
            "currentStep": workflow.current_step,
            "requestedStep": step_number,
        }), 400

    # Advance workflow if needed
    if workflow.current_step == 0:
        workflow.advance()

    data = request.json or {}
    executed_by = data.get("executed_by", "system")
    input_data = data.get("input_data", {})

    # Update step input and mark as started
    step.input_data = input_data
    step.start(executed_by)

    # Note: Actual step execution would be handled by an agent/service
    # This endpoint just marks the step as started
    # The agent would call /complete when done

    return jsonify({
        "step": step.to_dict(),
        "message": f"Step {step_number} ({step.step_type}) started",
    })


@workflow_bp.route("/<use_case_id>/workflow/steps/<int:step_number>/complete", methods=["POST"])
def complete_step(use_case_id: str, step_number: int):
    """
    Mark a workflow step as complete.

    Body must include:
    - output_data: dict of step output

    Optional:
    - requires_review: bool (override default HITL requirement)
    """
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    step = workflow.get_step(step_number)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    if step.status != WorkflowStepStatus.IN_PROGRESS.value:
        return jsonify({"error": "Step is not in progress"}), 400

    data = request.json or {}
    output_data = data.get("output_data", {})
    requires_review = data.get("requires_review")

    step.complete(output_data, requires_review)

    response = {
        "step": step.to_dict(),
        "message": f"Step {step_number} completed",
    }

    if step.requires_review:
        response["message"] = f"Step {step_number} completed, awaiting review"
        response["awaitingReview"] = True

    return jsonify(response)


@workflow_bp.route("/<use_case_id>/workflow/steps/<int:step_number>/fail", methods=["POST"])
def fail_step(use_case_id: str, step_number: int):
    """
    Mark a workflow step as failed.

    Body must include:
    - error: error message or dict
    """
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    step = workflow.get_step(step_number)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    data = request.json or {}
    error_data = data.get("error", {"message": "Unknown error"})
    if isinstance(error_data, str):
        error_data = {"message": error_data}

    step.fail(error_data)

    return jsonify({
        "step": step.to_dict(),
        "message": f"Step {step_number} marked as failed",
    })


@workflow_bp.route("/<use_case_id>/workflow/steps/<int:step_number>/review", methods=["POST"])
def review_step(use_case_id: str, step_number: int):
    """
    Submit HITL review for a workflow step.

    Body must include:
    - action: "approve" or "reject"
    - reviewer_id: who is reviewing

    Optional:
    - notes: review notes/comments
    """
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    step = workflow.get_step(step_number)
    if not step:
        return jsonify({"error": "Step not found"}), 404

    if step.status != WorkflowStepStatus.AWAITING_REVIEW.value:
        return jsonify({"error": "Step is not awaiting review"}), 400

    data = request.json or {}
    action = data.get("action")
    reviewer_id = data.get("reviewer_id", "unknown")
    notes = data.get("notes")

    if action == "approve":
        step.approve_review(reviewer_id, notes)
        # Advance workflow to next step
        workflow.advance()
        return jsonify({
            "step": step.to_dict(),
            "message": "Step approved",
            "nextStep": workflow.current_step,
        })
    elif action == "reject":
        if not notes:
            return jsonify({"error": "Rejection requires notes"}), 400
        step.reject_review(reviewer_id, notes)
        return jsonify({
            "step": step.to_dict(),
            "message": "Step rejected",
        })
    else:
        return jsonify({"error": "Invalid action, must be 'approve' or 'reject'"}), 400


@workflow_bp.route("/<use_case_id>/workflow/advance", methods=["POST"])
def advance_workflow(use_case_id: str):
    """Advance workflow to next step (if possible)."""
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    if not workflow.can_advance():
        current = workflow.get_current_step()
        reason = "Workflow completed" if workflow.status == "completed" else f"Step {workflow.current_step} not yet completed"
        return jsonify({
            "error": "Cannot advance workflow",
            "reason": reason,
            "currentStep": current.to_summary_dict() if current else None,
        }), 400

    next_step = workflow.advance()

    if next_step is None:
        return jsonify({
            "message": "Workflow completed",
            "progress": workflow.get_progress(),
        })

    return jsonify({
        "message": f"Advanced to step {workflow.current_step}",
        "currentStep": next_step.to_dict(),
        "progress": workflow.get_progress(),
    })


@workflow_bp.route("/<use_case_id>/workflow/rollback/<int:step_number>", methods=["POST"])
def rollback_workflow(use_case_id: str, step_number: int):
    """
    Roll back workflow to a specific step.
    All subsequent steps will be reset.
    """
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    if step_number < 1 or step_number > len(WORKFLOW_STEP_ORDER):
        return jsonify({"error": f"Invalid step number. Must be 1-{len(WORKFLOW_STEP_ORDER)}"}), 400

    success = workflow.rollback_to_step(step_number)
    if not success:
        return jsonify({"error": "Rollback failed"}), 500

    return jsonify({
        "message": f"Workflow rolled back to step {step_number}",
        "workflow": workflow.to_dict(),
        "progress": workflow.get_progress(),
    })


@workflow_bp.route("/<use_case_id>/workflow/progress", methods=["GET"])
def get_progress(use_case_id: str):
    """Get workflow progress summary."""
    workflow = Workflow.get_by_use_case(use_case_id)
    if not workflow:
        return jsonify({"error": "No workflow found"}), 404

    return jsonify(workflow.get_progress())
