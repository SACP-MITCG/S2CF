"""
BAC - Document upload and processing API
Handles business document uploads and AI-powered extraction
"""
from flask import Blueprint, request, jsonify, session, current_app
import os
import uuid
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)

# In-memory storage for uploaded documents (Phase 1-2)
DOCUMENT_STORE = {}

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "pptx", "xlsx", "md", "txt"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/", methods=["POST"])
def upload_document():
    """Upload a business document for processing."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"}), 400

    # Save file
    filename = secure_filename(file.filename)
    doc_id = str(uuid.uuid4())
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, f"{doc_id}_{filename}")
    file.save(filepath)

    # Process document (extract text, images, suggest template)
    from ..utilities.extractor import extract_document
    extraction_result = extract_document(filepath, filename)

    # Store in memory
    DOCUMENT_STORE[doc_id] = {
        "id": doc_id,
        "filename": filename,
        "filepath": filepath,
        "extraction": extraction_result,
    }

    # Store reference in session
    session["current_document"] = doc_id

    return jsonify({
        "documentId": doc_id,
        "filename": filename,
        "extraction": extraction_result,
    }), 201


@upload_bp.route("/<doc_id>", methods=["GET"])
def get_document(doc_id: str):
    """Get details of an uploaded document."""
    doc = DOCUMENT_STORE.get(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    return jsonify({
        "documentId": doc["id"],
        "filename": doc["filename"],
        "extraction": doc["extraction"],
    })


@upload_bp.route("/<doc_id>/suggest-template", methods=["POST"])
def suggest_template(doc_id: str):
    """Use AI to suggest the best template for this document."""
    doc = DOCUMENT_STORE.get(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    from ..utilities.ai_helper import suggest_template_for_document

    suggestion = suggest_template_for_document(doc["extraction"])

    return jsonify({
        "suggestedTemplate": suggestion["template_id"],
        "confidence": suggestion["confidence"],
        "reasoning": suggestion["reasoning"],
        "alternatives": suggestion.get("alternatives", []),
    })
