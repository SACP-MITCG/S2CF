"""Reference model endpoints."""

from flask import Blueprint, request, jsonify, current_app

models_bp = Blueprint("models", __name__)


@models_bp.route("", methods=["GET"])
def list_models():
    """List all reference models."""
    try:
        from app.services.vector_store import list_all_models
        models = list_all_models()
        return jsonify(models)
    except Exception as e:
        current_app.logger.error(f"List models error: {e}")
        return jsonify({"error": str(e)}), 500


@models_bp.route("", methods=["POST"])
def add_model():
    """Add a new reference model."""
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    if not name or not description:
        return jsonify({"error": "name and description are required"}), 400

    try:
        from app.services.vector_store import upsert_model

        vector_id = upsert_model(
            name=name,
            description=description,
            tags=data.get("tags", []),
        )

        return jsonify({
            "message": f"Model '{name}' added successfully",
            "id": vector_id,
        }), 201

    except Exception as e:
        current_app.logger.error(f"Add model error: {e}")
        return jsonify({"error": str(e)}), 500


@models_bp.route("/search", methods=["POST"])
def search_models():
    """Semantic search for reference models."""
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        from app.services.vector_store import query_models

        results = query_models(
            query=query,
            top_k=data.get("top_k", 5),
            min_score=data.get("min_score", 0.1),
        )

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results),
        })

    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500
