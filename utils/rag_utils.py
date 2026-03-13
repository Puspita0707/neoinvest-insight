"""
RAG utilities: chunking, embedding invocation, retrieval.
Embedding model is in models/embeddings.py; we use it here.
"""
import logging
from pathlib import Path
from typing import List, Tuple

from config.config import KNOWLEDGE_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RAG
from models.embeddings import get_embeddings

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    if not text or not text.strip():
        return []
    chunks = []
    start = 0
    text = text.strip()
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def load_documents_from_dir(directory: Path) -> List[Tuple[str, str]]:
    """Load .txt and .md files from directory. Returns list of (file_path, content)."""
    docs = []
    try:
        for path in directory.rglob("*"):
            if path.suffix.lower() in (".txt", ".md") and path.is_file():
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    if content.strip():
                        docs.append((str(path), content))
                except Exception as e:
                    logger.warning("Could not read %s: %s", path, e)
    except Exception as e:
        logger.warning("Error scanning knowledge dir %s: %s", directory, e)
    return docs


def chunk_documents(docs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Chunk each document. Returns list of (source_path, chunk_text)."""
    out = []
    for path, content in docs:
        for chunk in chunk_text(content):
            out.append((path, chunk))
    return out


def build_index(chunk_tuples: List[Tuple[str, str]]):
    """
    Build in-memory index: list of (source, chunk) and list of embedding vectors.
    Uses models/embeddings.get_embeddings.
    """
    if not chunk_tuples:
        return [], []
    texts = [c[1] for c in chunk_tuples]
    try:
        vectors = get_embeddings(texts)
    except Exception as e:
        logger.exception("Embedding failed: %s", e)
        return chunk_tuples, []
    return chunk_tuples, vectors


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    try:
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(x * x for x in b) ** 0.5
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
    except Exception:
        return 0.0


def retrieve(
    query: str,
    chunk_tuples: List[Tuple[str, str]],
    vectors: List[List[float]],
    top_k: int = TOP_K_RAG,
) -> List[str]:
    """
    Retrieve top_k most relevant chunks for query.
    Uses models/embeddings for query embedding.
    """
    if not chunk_tuples or not vectors or len(chunk_tuples) != len(vectors):
        return []
    try:
        q_vec = get_embeddings([query])[0]
    except Exception as e:
        logger.warning("Query embedding failed: %s", e)
        return []
    scored = [(cosine_similarity(q_vec, v), chunk_tuples[i][1]) for i, v in enumerate(vectors)]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:top_k]]


def load_and_index_knowledge_base():
    """
    Load from KNOWLEDGE_DIR, chunk, embed, return (chunk_tuples, vectors).
    Call from app at startup or when building RAG context.
    """
    docs = load_documents_from_dir(KNOWLEDGE_DIR)
    chunk_tuples = chunk_documents(docs)
    return build_index(chunk_tuples)
