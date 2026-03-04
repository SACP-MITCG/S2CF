"""
BAC - HOPEX Integration API
Proxy endpoints for browsing and linking to HOPEX architecture models
"""
from flask import Blueprint, request, jsonify
import os

hopex_bp = Blueprint("hopex", __name__)


@hopex_bp.route("/health", methods=["GET"])
def hopex_health():
    """Check if HOPEX integration is configured."""
    api_key = os.getenv("HOPEX_API_KEY")
    api_url = os.getenv("HOPEX_API_URL")

    return jsonify({
        "configured": bool(api_key and api_url),
        "apiUrl": api_url if api_url else None,
    })


@hopex_bp.route("/capabilities", methods=["GET"])
def list_capabilities():
    """List business capabilities from HOPEX."""
    from ..utilities.hopex.client import HopexClient

    try:
        client = HopexClient()
        capabilities = client.get_capabilities()
        return jsonify({"capabilities": capabilities})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hopex_bp.route("/processes", methods=["GET"])
def list_processes():
    """List business processes from HOPEX."""
    from ..utilities.hopex.client import HopexClient

    try:
        client = HopexClient()
        processes = client.get_processes()
        return jsonify({"processes": processes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hopex_bp.route("/applications", methods=["GET"])
def list_applications():
    """List applications from HOPEX."""
    from ..utilities.hopex.client import HopexClient

    try:
        client = HopexClient()
        applications = client.get_applications()
        return jsonify({"applications": applications})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hopex_bp.route("/diagrams", methods=["GET"])
def list_diagrams():
    """List diagrams from HOPEX."""
    from ..utilities.hopex.client import HopexClient

    element_id = request.args.get("elementId")
    diagram_type = request.args.get("type")

    try:
        client = HopexClient()
        diagrams = client.get_diagrams(element_id=element_id, diagram_type=diagram_type)
        return jsonify({"diagrams": diagrams})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hopex_bp.route("/diagrams/<diagram_id>/image", methods=["GET"])
def get_diagram_image(diagram_id: str):
    """Get diagram image from HOPEX."""
    from ..utilities.hopex.client import HopexClient

    try:
        client = HopexClient()
        image_data = client.get_diagram_image(diagram_id)
        return jsonify({
            "diagramId": diagram_id,
            "imageUrl": image_data.get("url"),
            "imageBase64": image_data.get("base64"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hopex_bp.route("/elements/<element_id>", methods=["GET"])
def get_element(element_id: str):
    """Get details of a specific HOPEX element."""
    from ..utilities.hopex.client import HopexClient

    try:
        client = HopexClient()
        element = client.get_element(element_id)
        return jsonify(element)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hopex_bp.route("/search", methods=["GET"])
def search_hopex():
    """Search HOPEX elements."""
    from ..utilities.hopex.client import HopexClient

    query = request.args.get("q", "")
    element_type = request.args.get("type")

    try:
        client = HopexClient()
        results = client.search(query=query, element_type=element_type)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
