"""
BAC - Export API
Handles exporting Use Case Descriptions to various formats
"""
from flask import Blueprint, request, jsonify, send_file
import io

export_bp = Blueprint("export", __name__)


@export_bp.route("/markdown/<use_case_id>", methods=["GET"])
def export_markdown(use_case_id: str):
    """Export use case as Markdown."""
    from ..models.irm import get_use_case
    from ..utilities.export_handlers import export_to_markdown

    use_case = get_use_case(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    markdown_content = export_to_markdown(use_case)

    # Return as downloadable file or JSON based on accept header
    if request.accept_mimetypes.accept_json:
        return jsonify({
            "format": "markdown",
            "content": markdown_content,
            "filename": f"{use_case.title.replace(' ', '_')}.md"
        })

    return send_file(
        io.BytesIO(markdown_content.encode('utf-8')),
        mimetype='text/markdown',
        as_attachment=True,
        download_name=f"{use_case.title.replace(' ', '_')}.md"
    )


@export_bp.route("/irm/<use_case_id>", methods=["GET"])
def export_irm_jsonld(use_case_id: str):
    """Export use case as IRM JSON-LD for SAC handover."""
    from ..models.irm import get_use_case
    from ..utilities.export_handlers import export_to_irm_jsonld

    use_case = get_use_case(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    irm_content = export_to_irm_jsonld(use_case)

    return jsonify(irm_content)


@export_bp.route("/word/<use_case_id>", methods=["GET"])
def export_word(use_case_id: str):
    """Export use case as Word document."""
    from ..models.irm import get_use_case
    from ..utilities.export_handlers import export_to_word

    use_case = get_use_case(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    try:
        word_buffer = export_to_word(use_case)

        return send_file(
            word_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f"{use_case.title.replace(' ', '_')}.docx"
        )
    except Exception as e:
        return jsonify({"error": f"Word export failed: {str(e)}"}), 500


@export_bp.route("/preview/<use_case_id>", methods=["GET"])
def export_preview(use_case_id: str):
    """Get export preview (structured summary) without generating file."""
    from ..models.irm import get_use_case

    use_case = get_use_case(use_case_id)
    if not use_case:
        return jsonify({"error": "Use case not found"}), 404

    # Generate preview summary
    preview = {
        "title": use_case.title,
        "sectionCount": len(use_case.sections),
        "bamReferenceCount": sum(len(s.bam_references) for s in use_case.sections),
        "sections": [
            {
                "id": s.id,
                "type": s.section_type,
                "title": s.title,
                "hasContent": bool(s.content),
                "bamReferenceCount": len(s.bam_references),
                "status": s.meta.status
            }
            for s in use_case.sections
        ],
        "availableFormats": ["markdown", "irm", "word"],
        "readyForExport": use_case.is_ready_for_export(),
        "exportWarnings": use_case.get_export_warnings()
    }

    return jsonify(preview)
