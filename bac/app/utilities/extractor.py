"""
BAC - Document Extraction Utility
Extracts text and images from business documents

Adapted from SAC extractor.py
"""
import os
import base64
from typing import Optional


def extract_document(filepath: str, filename: str) -> dict:
    """
    Extract text and images from a document.

    Args:
        filepath: Path to the uploaded file
        filename: Original filename

    Returns:
        Extraction result with text, images, and metadata
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    result = {
        "filename": filename,
        "extension": ext,
        "text": "",
        "images": [],
        "metadata": {},
        "suggestedSections": [],
    }

    try:
        if ext == "pdf":
            result = extract_pdf(filepath, result)
        elif ext in ("docx", "doc"):
            result = extract_docx(filepath, result)
        elif ext == "pptx":
            result = extract_pptx(filepath, result)
        elif ext in ("md", "txt"):
            result = extract_text(filepath, result)
        elif ext == "xlsx":
            result = extract_xlsx(filepath, result)
        else:
            result["error"] = f"Unsupported file type: {ext}"

    except Exception as e:
        result["error"] = str(e)

    return result


def extract_pdf(filepath: str, result: dict) -> dict:
    """Extract text and images from PDF using MarkItDown and PyMuPDF."""
    try:
        # Use MarkItDown for text extraction
        from markitdown import MarkItDown
        md = MarkItDown()
        md_result = md.convert(filepath)
        result["text"] = md_result.text_content if md_result else ""

        # Use PyMuPDF for image extraction
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(filepath)
            images = []

            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)

                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        # Filter small images (likely icons/logos)
                        width = base_image.get("width", 0)
                        height = base_image.get("height", 0)

                        if width >= 200 and height >= 200:  # Min size for diagrams
                            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                            images.append({
                                "page": page_num + 1,
                                "index": img_index,
                                "width": width,
                                "height": height,
                                "format": image_ext,
                                "base64": image_b64,
                            })

            doc.close()
            result["images"] = images[:10]  # Limit to 10 images

        except ImportError:
            pass  # PyMuPDF not installed

    except Exception as e:
        result["error"] = f"PDF extraction failed: {str(e)}"

    return result


def extract_docx(filepath: str, result: dict) -> dict:
    """Extract text from Word document using MarkItDown."""
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        md_result = md.convert(filepath)
        result["text"] = md_result.text_content if md_result else ""

    except Exception as e:
        result["error"] = f"DOCX extraction failed: {str(e)}"

    return result


def extract_pptx(filepath: str, result: dict) -> dict:
    """Extract text from PowerPoint using MarkItDown."""
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        md_result = md.convert(filepath)
        result["text"] = md_result.text_content if md_result else ""

    except Exception as e:
        result["error"] = f"PPTX extraction failed: {str(e)}"

    return result


def extract_text(filepath: str, result: dict) -> dict:
    """Extract plain text or markdown."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            result["text"] = f.read()
    except Exception as e:
        result["error"] = f"Text extraction failed: {str(e)}"

    return result


def extract_xlsx(filepath: str, result: dict) -> dict:
    """Extract text from Excel using MarkItDown."""
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        md_result = md.convert(filepath)
        result["text"] = md_result.text_content if md_result else ""

    except Exception as e:
        result["error"] = f"XLSX extraction failed: {str(e)}"

    return result
