"""
RAG embedding models. Used for vector embeddings of documents.
Invoked from app.py; embedding logic (chunking, retrieval) lives in utils.

This implementation uses a local SentenceTransformer model so that
no paid API key is required for embeddings.
"""
from functools import lru_cache
from typing import List, Optional

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Lazily load and cache the sentence-transformers model.
    """
    return SentenceTransformer(model_name)


def get_embeddings(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    """
    Get embedding vectors for a list of texts using a local model.
    """
    try:
        model_name = model or "all-MiniLM-L6-v2"
        sbert = _get_model(model_name)
        # encode returns a numpy array; convert to plain Python lists
        vectors = sbert.encode(texts, convert_to_numpy=True).tolist()
        return vectors
    except Exception as e:
        raise RuntimeError(f"Embedding error: {e}") from e


def embed_single(text: str, model: Optional[str] = None) -> List[float]:
    """Get embedding for a single string."""
    return get_embeddings([text], model=model)[0]
