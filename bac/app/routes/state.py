"""
BAC - IRM State Machine API Routes
Manages IRM object lifecycle state transitions with audit trail.
"""
from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.irm import (
    IRMState,
    IRM_STATE_TRANSITIONS,
    StateTransition,
)
from app.models.usecase_db import get_use_case_db

state_bp = Blueprint("state", __name__)


@state_bp.route("/<use_case_id>/state", methods=["GET"])
def get_state(use_case_id: str):
    """Get current state of a use case."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    current_state = use_case.get_state()
    valid_transitions = use_case.get_valid_transitions()

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": current_state.value,
        "validTransitions": [s.value for s in valid_transitions],
        "stateInfo": _get_state_info(current_state),
    })


@state_bp.route("/<use_case_id>/state", methods=["PUT"])
def transition_state(use_case_id: str):
    """
    Transition use case to a new state.

    Body must include:
    - state: target state value

    Optional:
    - triggered_by: user/system ID
    - reason: reason for transition
    - force: bypass validation (use with caution)
    """
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    target_state_str = data.get("state")

    if not target_state_str:
        return jsonify({"error": "Missing 'state' field"}), 400

    # Validate target state
    try:
        target_state = IRMState(target_state_str)
    except ValueError:
        valid_states = [s.value for s in IRMState]
        return jsonify({
            "error": f"Invalid state: {target_state_str}",
            "validStates": valid_states,
        }), 400

    triggered_by = data.get("triggered_by", "system")
    reason = data.get("reason")
    force = data.get("force", False)

    # Check if transition is valid
    if not force and not use_case.can_transition_to(target_state):
        current = use_case.get_state()
        valid = use_case.get_valid_transitions()
        return jsonify({
            "error": "Invalid state transition",
            "currentState": current.value,
            "requestedState": target_state.value,
            "validTransitions": [s.value for s in valid],
        }), 400

    # Perform transition
    success = use_case.transition_to(target_state, triggered_by, reason, force)

    if not success:
        return jsonify({"error": "Transition failed"}), 500

    return jsonify({
        "useCaseId": use_case_id,
        "previousState": data.get("_previous_state"),  # Will be None, but keeping for API consistency
        "currentState": target_state.value,
        "triggeredBy": triggered_by,
        "reason": reason,
    })


@state_bp.route("/<use_case_id>/state/history", methods=["GET"])
def get_state_history(use_case_id: str):
    """Get state transition history for a use case."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    history = use_case.get_state_history()

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "history": history,
    })


# ============================================
# Convenience endpoints for common transitions
# ============================================

@state_bp.route("/<use_case_id>/state/complete-extraction", methods=["POST"])
def complete_extraction(use_case_id: str):
    """Mark extraction as complete (EXTRACTING -> EXTRACTED)."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    triggered_by = data.get("triggered_by", "system")

    success = use_case.complete_extraction(triggered_by)
    if not success:
        return jsonify({
            "error": "Cannot complete extraction",
            "currentState": use_case.get_state().value,
            "hint": "Use case must be in EXTRACTING state",
        }), 400

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "message": "Extraction completed",
    })


@state_bp.route("/<use_case_id>/state/submit-for-review", methods=["POST"])
def submit_for_review(use_case_id: str):
    """Submit for HITL review (EXTRACTED/MODIFIED -> PENDING_REVIEW)."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    triggered_by = data.get("triggered_by", "system")

    success = use_case.submit_for_review(triggered_by)
    if not success:
        return jsonify({
            "error": "Cannot submit for review",
            "currentState": use_case.get_state().value,
            "hint": "Use case must be in EXTRACTED or MODIFIED state",
        }), 400

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "message": "Submitted for review",
    })


@state_bp.route("/<use_case_id>/state/start-review", methods=["POST"])
def start_review(use_case_id: str):
    """Start HITL review (PENDING_REVIEW -> IN_REVIEW)."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    reviewer_id = data.get("reviewer_id")

    if not reviewer_id:
        return jsonify({"error": "Missing 'reviewer_id' field"}), 400

    success = use_case.start_review(reviewer_id)
    if not success:
        return jsonify({
            "error": "Cannot start review",
            "currentState": use_case.get_state().value,
            "hint": "Use case must be in PENDING_REVIEW state",
        }), 400

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "reviewerId": reviewer_id,
        "message": "Review started",
    })


@state_bp.route("/<use_case_id>/state/approve", methods=["POST"])
def approve(use_case_id: str):
    """Approve use case (IN_REVIEW -> APPROVED)."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    reviewer_id = data.get("reviewer_id")
    reason = data.get("reason")

    if not reviewer_id:
        return jsonify({"error": "Missing 'reviewer_id' field"}), 400

    success = use_case.approve(reviewer_id, reason)
    if not success:
        return jsonify({
            "error": "Cannot approve",
            "currentState": use_case.get_state().value,
            "hint": "Use case must be in IN_REVIEW state",
        }), 400

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "approvedBy": reviewer_id,
        "message": "Use case approved",
    })


@state_bp.route("/<use_case_id>/state/reject", methods=["POST"])
def reject(use_case_id: str):
    """Reject use case (various states -> REJECTED)."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    reviewer_id = data.get("reviewer_id")
    reason = data.get("reason")

    if not reviewer_id:
        return jsonify({"error": "Missing 'reviewer_id' field"}), 400
    if not reason:
        return jsonify({"error": "Missing 'reason' field (required for rejection)"}), 400

    success = use_case.reject(reviewer_id, reason)
    if not success:
        return jsonify({
            "error": "Cannot reject from current state",
            "currentState": use_case.get_state().value,
        }), 400

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "rejectedBy": reviewer_id,
        "reason": reason,
        "message": "Use case rejected",
    })


@state_bp.route("/<use_case_id>/state/mark-modified", methods=["POST"])
def mark_modified(use_case_id: str):
    """Mark as modified (IN_REVIEW/APPROVED -> MODIFIED)."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    data = request.json or {}
    modifier_id = data.get("modifier_id", "system")
    reason = data.get("reason")

    success = use_case.mark_modified(modifier_id, reason)
    if not success:
        return jsonify({
            "error": "Cannot mark as modified",
            "currentState": use_case.get_state().value,
            "hint": "Use case must be in IN_REVIEW or APPROVED state",
        }), 400

    return jsonify({
        "useCaseId": use_case_id,
        "currentState": use_case.get_state().value,
        "modifiedBy": modifier_id,
        "message": "Marked as modified, needs re-review",
    })


# ============================================
# State machine info endpoints
# ============================================

@state_bp.route("/states", methods=["GET"])
def list_states():
    """List all possible IRM states with descriptions."""
    states = []
    for state in IRMState:
        states.append({
            "value": state.value,
            "info": _get_state_info(state),
            "validTransitions": [s.value for s in IRM_STATE_TRANSITIONS.get(state, [])],
        })

    return jsonify({"states": states})


@state_bp.route("/transitions", methods=["GET"])
def list_transitions():
    """Get the full state transition diagram."""
    transitions = {}
    for state, targets in IRM_STATE_TRANSITIONS.items():
        transitions[state.value] = [t.value for t in targets]

    return jsonify({
        "transitions": transitions,
        "terminalStates": ["rejected"],
        "initialState": "extracting",
    })


def _get_state_info(state: IRMState) -> dict:
    """Get human-readable info about a state."""
    info = {
        IRMState.EXTRACTING: {
            "label": "Extracting",
            "description": "Agent is processing and generating content",
            "isTerminal": False,
            "requiresHuman": False,
        },
        IRMState.EXTRACTED: {
            "label": "Extracted",
            "description": "Content created, ready for review queue",
            "isTerminal": False,
            "requiresHuman": False,
        },
        IRMState.PENDING_REVIEW: {
            "label": "Pending Review",
            "description": "Queued for human review",
            "isTerminal": False,
            "requiresHuman": True,
        },
        IRMState.IN_REVIEW: {
            "label": "In Review",
            "description": "Human is actively reviewing",
            "isTerminal": False,
            "requiresHuman": True,
        },
        IRMState.MODIFIED: {
            "label": "Modified",
            "description": "Changed after review, needs re-review",
            "isTerminal": False,
            "requiresHuman": False,
        },
        IRMState.APPROVED: {
            "label": "Approved",
            "description": "Human validated and approved",
            "isTerminal": False,  # Can still be modified
            "requiresHuman": False,
        },
        IRMState.REJECTED: {
            "label": "Rejected",
            "description": "Human rejected",
            "isTerminal": True,
            "requiresHuman": False,
        },
    }
    return info.get(state, {"label": state.value, "description": "Unknown state"})
