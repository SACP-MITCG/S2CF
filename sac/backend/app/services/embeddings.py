"""OpenAI embeddings service with connection pooling and retry logic."""

import os
from typing import List, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Singleton client for connection pooling
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """Get or create the OpenAI client singleton."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def get_embedding(
    text: str,
    model: Optional[str] = None,
    dimensions: Optional[int] = None,
) -> List[float]:
    """Generate embedding for text using text-embedding-3-large.

    Args:
        text: The text to embed.
        model: Optional model override.
        dimensions: Optional dimensions override (default 1024).

    Returns:
        List of floats representing the embedding vector.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    dimensions = dimensions or int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1024"))

    response = get_client().embeddings.create(
        model=model,
        input=text.strip(),
        dimensions=dimensions,
    )
    return response.data[0].embedding


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def get_embeddings_batch(
    texts: List[str],
    model: Optional[str] = None,
    dimensions: Optional[int] = None,
) -> List[List[float]]:
    """Generate embeddings for multiple texts in a single API call.

    Args:
        texts: List of texts to embed.
        model: Optional model override.
        dimensions: Optional dimensions override.

    Returns:
        List of embedding vectors in the same order as input.
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    cleaned = [t.strip() for t in texts if t and t.strip()]
    if not cleaned:
        raise ValueError("All texts are empty after cleaning")

    model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    dimensions = dimensions or int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1024"))

    response = get_client().embeddings.create(
        model=model,
        input=cleaned,
        dimensions=dimensions,
    )
    return [item.embedding for item in response.data]
