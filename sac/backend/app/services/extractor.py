"""PDF document extraction service."""

import os
import base64
from io import BytesIO
from typing import Dict, List, Tuple, Optional

from openai import OpenAI


def get_openai_client() -> OpenAI:
    """Get OpenAI client."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(pdf_buffer: BytesIO) -> str:
    """Extract text from PDF using markitdown.

    Args:
        pdf_buffer: PDF file as BytesIO.

    Returns:
        Extracted text in markdown format.
    """
    try:
        import markitdown as mid

        pdf_buffer.seek(0)
        processor = mid.MarkItDown()
        result = processor.convert_stream(pdf_buffer, file_extension="pdf")
        return result.markdown
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""


def extract_images_from_pdf(
    pdf_buffer: BytesIO,
    min_width: int = 600,
    min_height: int = 600,
) -> List[str]:
    """Extract images from PDF as base64 data URLs.

    Args:
        pdf_buffer: PDF file as BytesIO.
        min_width: Minimum image width to include.
        min_height: Minimum image height to include.

    Returns:
        List of base64 data URLs.
    """
    try:
        import fitz  # PyMuPDF
        from PIL import Image

        pdf_buffer.seek(0)
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")

        images = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            for img_info in image_list:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Load and check size
                img = Image.open(BytesIO(image_bytes))
                if img.width >= min_width and img.height >= min_height:
                    # Convert to PNG and base64
                    buffer = BytesIO()
                    img.convert("RGB").save(buffer, format="PNG")
                    b64 = base64.b64encode(buffer.getvalue()).decode()
                    images.append(f"data:image/png;base64,{b64}")

        return images

    except Exception as e:
        print(f"Error extracting images: {e}")
        return []


def generate_recommendation(
    text: str,
    images: Optional[List[str]] = None,
) -> str:
    """Generate architecture recommendation using GPT-4o.

    Args:
        text: Extracted document text.
        images: Optional list of image data URLs.

    Returns:
        AI-generated recommendation.
    """
    client = get_openai_client()

    content = [
        {
            "type": "text",
            "text": f"{text[:8000]}\n\nBased on this document, recommend the most suitable architecture reference model.",
        }
    ]

    if images:
        for img_url in images[:3]:  # Limit to 3 images
            content.append({
                "type": "image_url",
                "image_url": {"url": img_url},
            })

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a software architecture expert. Analyze the document and recommend an appropriate architecture reference model.",
                },
                {"role": "user", "content": content},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating recommendation: {e}")
        return "Unable to generate recommendation."


def extract_and_analyze(pdf_buffer: BytesIO) -> Dict:
    """Extract content from PDF and generate recommendation.

    Args:
        pdf_buffer: PDF file as BytesIO.

    Returns:
        Dictionary with text, images, and recommendation.
    """
    text = extract_text_from_pdf(pdf_buffer)
    images = extract_images_from_pdf(pdf_buffer)
    recommendation = generate_recommendation(text, images)

    return {
        "text": text,
        "images": images,
        "recommendation": recommendation,
    }
