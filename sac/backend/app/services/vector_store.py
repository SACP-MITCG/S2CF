"""Vector store service using pgvector (PostgreSQL extension).

Stores reference architecture models with embeddings for semantic search.
Uses existing PostgreSQL infrastructure - no external API keys needed.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from app.services.embeddings import get_embedding

# Connection pool singleton
_conn: Optional[psycopg.Connection] = None


def get_connection() -> psycopg.Connection:
    """Get or create database connection with pgvector support."""
    global _conn

    if _conn is None or _conn.closed:
        database_url = os.getenv("DATABASE_URL", "postgresql://sacp:localdev@localhost:5432/sacp")
        _conn = psycopg.connect(database_url)
        register_vector(_conn)
        _ensure_table_exists(_conn)

    return _conn


def _ensure_table_exists(conn: psycopg.Connection) -> None:
    """Create the reference_models table if it doesn't exist."""
    with conn.cursor() as cur:
        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Create table for reference models
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reference_models (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                tags TEXT[] DEFAULT '{}',
                source VARCHAR(100) DEFAULT 'manual',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding vector(1024)
            )
        """)

        # Create index for vector similarity search (HNSW for performance)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS reference_models_embedding_idx
            ON reference_models
            USING hnsw (embedding vector_cosine_ops)
        """)

        conn.commit()


def upsert_model(
    name: str,
    description: str,
    tags: Optional[List[str]] = None,
    source: str = "manual",
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Add or update a reference model with embedding.

    Args:
        name: Model name.
        description: Model description.
        tags: Optional list of tags.
        source: Source of the model.
        additional_metadata: Not used (kept for API compatibility).

    Returns:
        The model ID.
    """
    if tags is None:
        tags = []

    # Generate embedding from name + description
    embedding_text = f"{name}: {description}"
    embedding = np.array(get_embedding(embedding_text))

    # Create deterministic ID from name
    model_id = f"model_{name.lower().replace(' ', '_').replace('-', '_')}"

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO reference_models (id, name, description, tags, source, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                tags = EXCLUDED.tags,
                source = EXCLUDED.source,
                embedding = EXCLUDED.embedding,
                added_at = CURRENT_TIMESTAMP
        """, (model_id, name, description, tags, source, embedding))
        conn.commit()

    return model_id


def query_models(
    query: str,
    top_k: int = 5,
    min_score: float = 0.0,
    filter_dict: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Semantic search for reference models.

    Args:
        query: Search query text.
        top_k: Maximum number of results.
        min_score: Minimum similarity score (0-1). Note: pgvector returns distance, we convert.
        filter_dict: Not used (kept for API compatibility).

    Returns:
        List of matching models with scores.
    """
    query_embedding = np.array(get_embedding(query))

    conn = get_connection()
    with conn.cursor() as cur:
        # Use cosine distance (1 - cosine_similarity)
        # So we convert: similarity = 1 - distance
        cur.execute("""
            SELECT
                id, name, description, tags, source, added_at,
                1 - (embedding <=> %s) as similarity
            FROM reference_models
            WHERE 1 - (embedding <=> %s) >= %s
            ORDER BY embedding <=> %s
            LIMIT %s
        """, (query_embedding, query_embedding, min_score, query_embedding, top_k))

        rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2] or "",
            "tags": row[3] or [],
            "source": row[4] or "manual",
            "addedAt": row[5].isoformat() if row[5] else "",
            "score": round(row[6], 4),
        }
        for row in rows
    ]


def list_all_models(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch all reference models.

    Args:
        limit: Maximum number of models to return.

    Returns:
        List of all models.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, description, tags, source, added_at
            FROM reference_models
            ORDER BY added_at DESC
            LIMIT %s
        """, (limit,))

        rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2] or "",
            "tags": row[3] or [],
            "source": row[4] or "manual",
            "addedAt": row[5].isoformat() if row[5] else "",
        }
        for row in rows
    ]


def delete_model(model_id: str) -> bool:
    """Delete a reference model by ID.

    Args:
        model_id: The model ID to delete.

    Returns:
        True if deletion was successful.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reference_models WHERE id = %s", (model_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"Error deleting model {model_id}: {e}")
        return False


def close_connection() -> None:
    """Close the database connection."""
    global _conn
    if _conn and not _conn.closed:
        _conn.close()
        _conn = None
