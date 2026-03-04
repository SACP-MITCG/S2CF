"""
BAC - Use Case CRUD API
Manages Business Use Case Descriptions stored in PostgreSQL
"""
from flask import Blueprint, request, jsonify, session
from ..models.usecase_db import (
    create_use_case_db,
    get_use_case_db,
    update_use_case_db,
    delete_use_case_db,
    list_use_cases_db,
)
from app.extensions import db

usecases_bp = Blueprint("usecases", __name__)


@usecases_bp.route("/", methods=["GET"])
def list_usecases():
    """List all use cases."""
    use_cases = list_use_cases_db()
    return jsonify({"useCases": use_cases})


@usecases_bp.route("/", methods=["POST"])
def create_usecase():
    """Create a new use case from a template or blank."""
    data = request.json or {}
    template_id = data.get("templateId")
    title = data.get("title", "New Use Case")

    use_case = create_use_case_db(
        session_id=session.get("session_id"),
        title=title,
        template_id=template_id
    )

    return jsonify(use_case.to_dict()), 201


@usecases_bp.route("/<use_case_id>", methods=["GET"])
def get_usecase(use_case_id: str):
    """Get a specific use case by ID."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404
    return jsonify(use_case.to_dict())


@usecases_bp.route("/<use_case_id>", methods=["PUT"])
def update_usecase(use_case_id: str):
    """Update a use case."""
    data = request.json or {}
    use_case = update_use_case_db(use_case_id, data)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404
    return jsonify(use_case.to_dict())


@usecases_bp.route("/<use_case_id>", methods=["DELETE"])
def delete_usecase(use_case_id: str):
    """Delete a use case."""
    success = delete_use_case_db(use_case_id)
    if not success:
        return jsonify({"error": "Use case not found"}), 404
    return jsonify({"deleted": True})


@usecases_bp.route("/<use_case_id>/sections", methods=["POST"])
def add_section(use_case_id: str):
    """Add a new section to a use case."""
    data = request.json or {}
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    section = use_case.add_section(
        section_type=data.get("type", "Overview"),
        title=data.get("title", "New Section"),
        content=data.get("content", "")
    )
    db.session.commit()

    return jsonify(section), 201


@usecases_bp.route("/<use_case_id>/sections/<section_id>", methods=["PUT"])
def update_section(use_case_id: str, section_id: str):
    """Update a section in a use case."""
    data = request.json or {}
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    section = use_case.update_section(section_id, data)
    if not section:
        return jsonify({"error": "Section not found"}), 404

    db.session.commit()
    return jsonify(section)


@usecases_bp.route("/<use_case_id>/sections/<section_id>", methods=["DELETE"])
def delete_section(use_case_id: str, section_id: str):
    """Delete a section from a use case."""
    use_case = get_use_case_db(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    success = use_case.delete_section(section_id)
    if not success:
        return jsonify({"error": "Section not found"}), 404

    db.session.commit()
    return jsonify({"deleted": True})
