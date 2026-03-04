"""Chat endpoints with RAG support."""

from flask import Blueprint, request, jsonify, current_app

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("", methods=["POST"])
def chat():
    """Send a chat message and get a response.

    Request body:
        message: The user's message
        session_id: Optional session ID for conversation continuity
        document_id: Optional document ID for context
    """
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    session_id = data.get("session_id") or request.remote_addr
    document_id = data.get("document_id")

    try:
        # Import here to avoid circular imports
        from app.services.langchain import run_chat
        from app.models.document import Document

        # Get document context if provided
        document_context = None
        if document_id:
            doc = Document.get_by_id(document_id)
            if doc:
                document_context = doc.content

        response = run_chat(
            session_id=session_id,
            message=message,
            document_context=document_context,
        )

        return jsonify({
            "response": response,
            "session_id": session_id,
        })

    except Exception as e:
        current_app.logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/history/<session_id>", methods=["GET"])
def get_history(session_id: str):
    """Get chat history for a session."""
    try:
        from app.services.langchain import get_chat_history
        history = get_chat_history(session_id)
        return jsonify({"history": history, "session_id": session_id})
    except Exception as e:
        current_app.logger.error(f"History error: {e}")
        return jsonify({"error": str(e)}), 500
