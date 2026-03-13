"""
Live web search: real-time search when LLM lacks knowledge.
API keys in config/; provider: serpapi | tavily | brave.
"""
import logging
from typing import List, Optional

from config.config import (
    WEB_SEARCH_PROVIDER,
    SERPAPI_API_KEY,
    TAVILY_API_KEY,
    BRAVE_API_KEY,
)

logger = logging.getLogger(__name__)


def live_web_search(query: str, num_results: int = 6) -> str:
    """
    Perform real-time web search and return a single string summary of results
    for the LLM to use. Used when the model needs current info (e.g. stock prices, news).
    """
    try:
        if WEB_SEARCH_PROVIDER == "tavily" and TAVILY_API_KEY:
            return _search_tavily(query, num_results)
        if WEB_SEARCH_PROVIDER == "serpapi" and SERPAPI_API_KEY:
            return _search_serpapi(query, num_results)
        if WEB_SEARCH_PROVIDER == "brave" and BRAVE_API_KEY:
            return _search_brave(query, num_results)
        logger.warning("No valid web search provider or API key configured.")
        return ""
    except Exception as e:
        logger.exception("Web search failed: %s", e)
        return f"[Web search error: {e}]"


def _search_tavily(query: str, num_results: int) -> str:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        r = client.search(query, max_results=num_results, include_answer=True)
        parts = []
        if r.get("answer"):
            parts.append(f"Summary: {r['answer']}")
        for item in r.get("results", [])[:num_results]:
            title = item.get("title", "")
            content = item.get("content", "")
            url = item.get("url", "")
            parts.append(f"- {title}\n  {content}\n  Source: {url}")
        return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.exception("Tavily search failed: %s", e)
        return f"[Tavily error: {e}]"


def _search_serpapi(query: str, num_results: int) -> str:
    try:
        from serpapi import GoogleSearch
        params = {"q": query, "api_key": SERPAPI_API_KEY, "num": num_results}
        search = GoogleSearch(params)
        data = search.get_dict()
        parts = []
        for obj in data.get("organic_results", [])[:num_results]:
            title = obj.get("title", "")
            snippet = obj.get("snippet", "")
            link = obj.get("link", "")
            parts.append(f"- {title}\n  {snippet}\n  Source: {link}")
        return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.exception("SerpAPI search failed: %s", e)
        return f"[SerpAPI error: {e}]"


def _search_brave(query: str, num_results: int) -> str:
    try:
        import requests
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
        params = {"q": query, "count": num_results}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        parts = []
        for obj in data.get("web", {}).get("results", [])[:num_results]:
            title = obj.get("title", "")
            desc = obj.get("description", "")
            link = obj.get("url", "")
            parts.append(f"- {title}\n  {desc}\n  Source: {link}")
        return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.exception("Brave search failed: %s", e)
        return f"[Brave error: {e}]"
