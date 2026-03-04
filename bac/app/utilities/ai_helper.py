"""
BAC - AI Helper Utilities
GPT-4o powered content generation and analysis
"""
import os
import json
from typing import Optional

from openai import OpenAI


def get_openai_client() -> OpenAI:
    """Get configured OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)


def suggest_template_for_document(extraction: dict) -> dict:
    """
    Analyze document extraction and suggest the best template.

    Args:
        extraction: Document extraction result with text and metadata

    Returns:
        Template suggestion with confidence and reasoning
    """
    text = extraction.get("text", "")[:8000]  # Limit context

    if not text.strip():
        return {
            "template_id": "blank",
            "confidence": 0.5,
            "reasoning": "No text content extracted from document",
            "alternatives": []
        }

    client = get_openai_client()

    prompt = f"""Analyze this business document and recommend the most appropriate template for creating a Business Use Case Description.

Available templates:
1. regulatory_change - For use cases driven by regulatory/compliance requirements
2. process_improvement - For optimizing existing business processes
3. new_capability - For adding new business capabilities
4. integration - For system integration use cases
5. blank - For documents that don't fit other categories

Document content:
{text}

Respond with JSON:
{{
    "template_id": "template name",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "alternatives": ["other", "options"]
}}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        return {
            "template_id": "blank",
            "confidence": 0.3,
            "reasoning": f"AI analysis failed: {str(e)}",
            "alternatives": ["regulatory_change", "process_improvement", "new_capability"]
        }


def generate_section_content(
    section_type: str,
    section_title: str,
    document_text: str,
    existing_content: str = "",
    instructions: str = ""
) -> dict:
    """
    Generate or enhance section content using AI.

    Args:
        section_type: Type of section (Overview, Objectives, etc.)
        section_title: Title of the section
        document_text: Source document text for context
        existing_content: Any existing content to build upon
        instructions: Additional user instructions

    Returns:
        Generated content with source attribution
    """
    client = get_openai_client()

    context = document_text[:6000] if document_text else ""

    prompt = f"""You are a Business Analyst assistant helping to write a Business Use Case Description.

Section Type: {section_type}
Section Title: {section_title}

Source Document Context:
{context}

{"Existing Content to enhance:" if existing_content else ""}
{existing_content if existing_content else ""}

{"User Instructions: " + instructions if instructions else ""}

Generate professional content for this section. Use Markdown formatting.
Include specific details from the source document where relevant.
Mark any AI-generated suggestions that need human verification with [VERIFY].

Respond with JSON:
{{
    "content": "generated markdown content",
    "sources": ["list of specific phrases/sections from source doc used"],
    "suggestions": ["additional items the BA should consider"]
}}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        return {
            "content": existing_content or f"_Failed to generate content: {str(e)}_",
            "sources": [],
            "suggestions": []
        }


def extract_objectives_from_text(text: str) -> list[dict]:
    """
    Extract potential SMART objectives from document text.

    Args:
        text: Document text to analyze

    Returns:
        List of extracted objectives with confidence scores
    """
    client = get_openai_client()

    prompt = f"""Analyze this business document and extract potential SMART objectives.

For each objective found, identify:
- The specific goal
- How it could be measured
- The target or deadline if mentioned
- Confidence that this is a real objective (not just descriptive text)

Document:
{text[:6000]}

Respond with JSON:
{{
    "objectives": [
        {{
            "description": "objective text",
            "specific": "what specifically",
            "measurable": "how to measure",
            "target": "target value or deadline",
            "source_quote": "exact quote from document",
            "confidence": 0.0-1.0
        }}
    ]
}}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("objectives", [])

    except Exception as e:
        return []


def extract_user_journeys_from_text(text: str) -> list[dict]:
    """
    Extract potential user journeys from document text.

    Args:
        text: Document text to analyze

    Returns:
        List of extracted user journeys
    """
    client = get_openai_client()

    prompt = f"""Analyze this business document and extract potential user journeys or process flows.

For each journey found, identify:
- The actor/user performing the journey
- The goal they're trying to achieve
- The main steps
- Any decision points or branches

Document:
{text[:6000]}

Respond with JSON:
{{
    "journeys": [
        {{
            "actor": "who performs this",
            "goal": "what they want to achieve",
            "steps": ["step 1", "step 2"],
            "decisions": ["decision point 1"],
            "source_section": "where in doc this was found",
            "confidence": 0.0-1.0
        }}
    ]
}}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("journeys", [])

    except Exception as e:
        return []
