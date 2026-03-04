"""Document CRUD endpoints."""

from io import BytesIO
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.models.document import Document

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("", methods=["GET"])
def list_documents():
    """List all documents."""
    source = request.args.get("source")
    docs = Document.get_all(source=source)
    return jsonify([doc.to_dict() for doc in docs])


@documents_bp.route("/<doc_id>", methods=["GET"])
def get_document(doc_id: str):
    """Get a specific document."""
    doc = Document.get_by_id(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc.to_dict())


@documents_bp.route("/upload", methods=["POST"])
def upload_document():
    """Upload a PDF document and extract content."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)

    try:
        # Read file into buffer
        pdf_buffer = BytesIO()
        file.save(pdf_buffer)
        pdf_buffer.seek(0)

        # Extract content and generate recommendation
        from app.services.extractor import extract_and_analyze
        result = extract_and_analyze(pdf_buffer)

        doc = Document.create(
            filename=filename,
            content=result["text"],
            recommendation=result["recommendation"],
            source="upload",
        )

        return jsonify({
            "message": f"{filename} uploaded successfully",
            "document_id": doc.id,
            "recommendation": result["recommendation"],
        }), 201

    except Exception as e:
        current_app.logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500
