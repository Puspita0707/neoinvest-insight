"""
Configuration and API keys for Investment Research Assistant.
Use environment variables; do not commit secrets.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover - used only in Streamlit runtime
    st = None  # type: ignore


def _get_setting(name: str, default: str = "") -> str:
    """
    Read config values in this order:
    1) Streamlit Cloud secrets (st.secrets)
    2) Environment variables (os.getenv)
    """
    # 1) Streamlit secrets (for deployed app)
    if st is not None:
        try:
            secrets = getattr(st, "secrets", None)
            if secrets is not None and name in secrets:
                return str(secrets[name])
        except Exception:
            # If secrets are not available for any reason, fall back to env vars
            pass

    # 2) Standard environment variables (for local dev)
    return os.getenv(name, default)


# Load .env once at import time so Streamlit and local runs both see it
load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"

# LLM providers - set one via env
# OpenAI is disabled for this project to avoid paid usage.
# Even if OPENAI_API_KEY is set in the environment, it is ignored here.
OPENAI_API_KEY = ""
GROQ_API_KEY = _get_setting("GROQ_API_KEY", "")
GOOGLE_API_KEY = _get_setting("GOOGLE_API_KEY", "")  # for Gemini

# Default LLM provider: openai | groq | gemini
LLM_PROVIDER = _get_setting("LLM_PROVIDER", "openai")

# Embeddings (for RAG) - OpenAI is common; can add others
EMBEDDING_MODEL = _get_setting("EMBEDDING_MODEL", "text-embedding-3-small")

# Live web search - SerpAPI, Tavily, or Brave
SERPAPI_API_KEY = _get_setting("SERPAPI_API_KEY", "")
TAVILY_API_KEY = _get_setting("TAVILY_API_KEY", "")
BRAVE_API_KEY = _get_setting("BRAVE_API_KEY", "")

# YouTube search (optional) - Google API
YOUTUBE_API_KEY = _get_setting("YOUTUBE_API_KEY", "")

# Search provider: serpapi | tavily | brave (brave often has free tier)
WEB_SEARCH_PROVIDER = _get_setting("WEB_SEARCH_PROVIDER", "tavily")

# RAG settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K_RAG = int(os.getenv("TOP_K_RAG", "4"))

# Ensure dirs exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
