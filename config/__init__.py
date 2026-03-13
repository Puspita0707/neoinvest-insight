# Re-export config symbols for "from config import ..."
from .config import (
    PROJECT_ROOT,
    DATA_DIR,
    KNOWLEDGE_DIR,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
    EMBEDDING_MODEL,
    WEB_SEARCH_PROVIDER,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RAG,
)
