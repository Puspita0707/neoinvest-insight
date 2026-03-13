"""
LLM models: OpenAI, Groq, Google Gemini.
Invoked from app.py; provider selected via config.
"""
import os
from typing import Generator, Optional

from config.config import LLM_PROVIDER, OPENAI_API_KEY, GROQ_API_KEY, GOOGLE_API_KEY


def get_chat_completion(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    """Get a single completion from the configured LLM provider."""
    try:
        if LLM_PROVIDER == "openai":
            return _openai_chat(messages, model or "gpt-4o-mini", temperature, max_tokens)
        if LLM_PROVIDER == "groq":
            return _groq_chat(messages, model or "llama-3.1-8b-instant", temperature, max_tokens)
        if LLM_PROVIDER == "gemini":
            return _gemini_chat(messages, model or "gemini-1.5-flash", temperature, max_tokens)
        return "Error: Set LLM_PROVIDER to openai, groq, or gemini and provide the corresponding API key."
    except Exception as e:
        return f"LLM error: {str(e)}"


def get_chat_stream(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Generator[str, None, None]:
    """Stream completion tokens from the configured LLM provider."""
    try:
        if LLM_PROVIDER == "openai":
            yield from _openai_stream(messages, model or "gpt-4o-mini", temperature, max_tokens)
        elif LLM_PROVIDER == "groq":
            yield from _groq_stream(messages, model or "llama-3.1-8b-instant", temperature, max_tokens)
        elif LLM_PROVIDER == "gemini":
            yield from _gemini_stream(messages, model or "gemini-1.5-flash", temperature, max_tokens)
        else:
            yield "Error: Set LLM_PROVIDER and API key in config."
    except Exception as e:
        yield f"LLM error: {str(e)}"


def _openai_chat(messages: list, model: str, temperature: float, max_tokens: Optional[int]) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    kwargs = {"model": model, "messages": messages, "temperature": temperature}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    r = client.chat.completions.create(**kwargs)
    return r.choices[0].message.content or ""


def _openai_stream(messages: list, model: str, temperature: float, max_tokens: Optional[int]) -> Generator[str, None, None]:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    kwargs = {"model": model, "messages": messages, "temperature": temperature, "stream": True}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    stream = client.chat.completions.create(**kwargs)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _groq_chat(messages: list, model: str, temperature: float, max_tokens: Optional[int]) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    kwargs = {"model": model, "messages": messages, "temperature": temperature}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    r = client.chat.completions.create(**kwargs)
    return r.choices[0].message.content or ""


def _groq_stream(messages: list, model: str, temperature: float, max_tokens: Optional[int]) -> Generator[str, None, None]:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    kwargs = {"model": model, "messages": messages, "temperature": temperature, "stream": True}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    stream = client.chat.completions.create(**kwargs)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _gemini_chat(messages: list, model: str, temperature: float, max_tokens: Optional[int]) -> str:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini = genai.GenerativeModel(model)
    # Convert OpenAI-style messages to Gemini format
    parts = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        parts.append({"role": role, "parts": [m["content"]]})
    chat = gemini.start_chat(history=parts[:-1] if len(parts) > 1 else [])
    response = chat.send_message(parts[-1]["parts"][0])
    return response.text


def _gemini_stream(messages: list, model: str, temperature: float, max_tokens: Optional[int]) -> Generator[str, None, None]:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini = genai.GenerativeModel(model)
    parts = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        parts.append({"role": role, "parts": [m["content"]]})
    chat = gemini.start_chat(history=parts[:-1] if len(parts) > 1 else [])
    response = chat.send_message(parts[-1]["parts"][0], stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text
