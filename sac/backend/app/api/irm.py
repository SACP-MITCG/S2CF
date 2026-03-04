"""IRM import endpoint for BAC integration."""

from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Dict, Any

from app.extensions import db
from app.models.document import Document

irm_bp = Blueprint("irm", __name__)


class IRMSection(BaseModel):
    """IRM section schema."""
    id: str
    name: str
    content: str = ""
    order: int = 0


class IRMImport(BaseModel):
    """IRM JSON-LD import schema."""
    id: str
    name: str
    description: str = ""
    template: Optional[str] = None
    sections: List[IRMSection] = Field(default_factory=list)
    objectives: List[str] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)
    main_flow: List[str] = Field(default_factory=list)
    alternative_flows: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert IRM to markdown format."""
        lines = [f"# {self.name}", ""]
        if self.description:
            lines.extend([self.description, ""])
        if self.objectives:
            lines.extend(["## Objectives", ""])
            for obj in self.objectives:
                lines.append(f"- {obj}")
            lines.append("")
        if self.actors:
            lines.extend(["## Actors", ""])
            for actor in self.actors:
                lines.append(f"- {actor}")
            lines.append("")
        if self.main_flow:
            lines.extend(["## Main Flow", ""])
            for i, step in enumerate(self.main_flow, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        for section in sorted(self.sections, key=lambda s: s.order):
            lines.extend([f"## {section.name}", "", section.content, ""])
        return "\n".join(lines)


@irm_bp.route("/import", methods=["POST"])
def import_irm():
    """Import IRM JSON-LD from BAC."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            irm = IRMImport(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation failed", "details": e.errors()}), 400

        markdown_content = irm.to_markdown()

        doc = Document.create(
            filename=f"irm_{irm.id}.json",
            content=markdown_content,
            metadata={
                "source": "bac",
                "irm_id": irm.id,
                "name": irm.name,
                "template": irm.template,
            },
            source="bac",
            irm_id=irm.id,
        )

        current_app.logger.info(f"IRM {irm.id} imported as document {doc.id}")

        return jsonify({
            "message": "IRM imported successfully",
            "document_id": doc.id,
            "irm_id": irm.id,
            "name": irm.name,
        }), 201

    except Exception as e:
        current_app.logger.error(f"IRM import error: {e}")
        return jsonify({"error": str(e)}), 500


@irm_bp.route("/documents", methods=["GET"])
def list_irm_documents():
    """List all documents imported from BAC."""
    docs = Document.get_all(source="bac")
    return jsonify([doc.to_dict() for doc in docs])
