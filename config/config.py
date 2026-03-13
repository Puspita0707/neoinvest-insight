"""
Configuration and API keys for Investment Research Assistant.
Use environment variables; do not commit secrets.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

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
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  # for Gemini

# Default LLM provider: openai | groq | gemini
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# Embeddings (for RAG) - OpenAI is common; can add others
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Live web search - SerpAPI, Tavily, or Brave
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")

# YouTube search (optional) - Google API
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Search provider: serpapi | tavily | brave (brave often has free tier)
WEB_SEARCH_PROVIDER = os.getenv("WEB_SEARCH_PROVIDER", "tavily")

# RAG settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K_RAG = int(os.getenv("TOP_K_RAG", "4"))

# Ensure dirs exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
