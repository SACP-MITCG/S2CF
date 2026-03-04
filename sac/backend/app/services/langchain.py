"""LangChain chat service with Redis-backed session memory."""

import os
from typing import Optional, List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.services.vector_store import query_models

# In-memory fallback for development
_session_memory: Dict[str, ChatMessageHistory] = {}


def _get_memory(session_id: str) -> ChatMessageHistory:
    """Get chat memory for session (Redis or in-memory fallback)."""
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        try:
            from langchain_community.chat_message_histories import RedisChatMessageHistory
            return RedisChatMessageHistory(
                session_id=f"sac:session:{session_id}",
                url=redis_url,
                ttl=3600 * 24,  # 24 hour TTL
            )
        except Exception as e:
            print(f"Redis unavailable, using in-memory: {e}")

    # Fallback to in-memory
    if session_id not in _session_memory:
        _session_memory[session_id] = ChatMessageHistory()
    return _session_memory[session_id]


def get_session_memory(session_id: str) -> ChatMessageHistory:
    """Get isolated memory for a session."""
    return _get_memory(session_id)


def clear_session_memory(session_id: str) -> None:
    """Clear memory for a session."""
    memory = get_session_memory(session_id)
    memory.clear()
    if session_id in _session_memory:
        del _session_memory[session_id]


def _build_system_prompt(document_context: Optional[str], model_context: str) -> str:
    """Build system prompt with context."""
    return f"""You are a solution architecture assistant helping users design software systems.

## Available Context

### Uploaded Document
{document_context or "No document has been uploaded."}

### Relevant Reference Models
{model_context or "No matching reference models found."}

## Instructions
- If the user asks about "the document" or "uploaded file", answer using the Document section.
- If the user asks about "reference models" or architectures, use the Reference Models section.
- Be concise and accurate. Cite specific parts when relevant.
- If you don't have enough information, say so."""


def run_chat(
    session_id: str,
    message: str,
    document_context: Optional[str] = None,
    top_k_models: int = 5,
    min_model_score: float = 0.3,
    temperature: float = 0.7,
) -> str:
    """Run RAG-enhanced chat with memory isolation.

    Args:
        session_id: Unique session identifier.
        message: User's message.
        document_context: Optional document context.
        top_k_models: Number of reference models to retrieve.
        min_model_score: Minimum similarity score for models.
        temperature: LLM temperature.

    Returns:
        Assistant's response.
    """
    # Retrieve relevant reference models via semantic search
    try:
        relevant_models = query_models(message, top_k=top_k_models, min_score=min_model_score)
        model_context = "\n".join([
            f"- **{m['name']}** (score: {m['score']}): {m['description']}"
            for m in relevant_models
        ]) if relevant_models else "No matching reference models found."
    except Exception as e:
        print(f"Error querying models: {e}")
        model_context = "Unable to retrieve reference models."

    system_prompt = _build_system_prompt(document_context, model_context)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=temperature,
    )

    chain = RunnableWithMessageHistory(
        prompt | llm,
        get_session_memory,
        input_messages_key="input",
        history_messages_key="history",
    )

    result = chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )

    return result.content


def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """Get chat history for a session."""
    memory = get_session_memory(session_id)
    return [
        {"role": msg.type, "content": msg.content}
        for msg in memory.messages
    ]
