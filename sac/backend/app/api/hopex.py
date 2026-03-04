"""HOPEX mock export endpoint."""

from flask import Blueprint, request, jsonify

hopex_bp = Blueprint("hopex", __name__)


@hopex_bp.route("/export", methods=["POST"])
def export_to_hopex():
    """Mock HOPEX export endpoint.

    In production, this would create an application in HOPEX.
    For now, returns a simulated response.
    """
    data = request.get_json() or {}

    return jsonify({
        "status": "mock",
        "message": "HOPEX export simulated (no credentials configured)",
        "application": {
            "id": "mock-app-001",
            "name": data.get("name", "New Application"),
            "code": "APP-001",
            "type": "InHouseApplication",
            "status": "created",
        },
        "diagram": {
            "type": "Mermaid",
            "content": "flowchart TD\\n    A[Start] --> B[Process] --> C[End]",
        },
    })
