import textwrap

from utils.rag_utils import load_and_index_knowledge_base, retrieve


def main():
    """
    Tiny helper script to inspect RAG retrieval for a few queries.

    Run with:
        python eval_rag.py

    Then manually judge how many of the top-3 chunks are relevant
    for each question to estimate Precision@3.
    """
    questions = [
        "Explain the key differences between NSE/BSE and US markets.",
        "What are the main stock indices in Indian markets?",
        "How can a beginner diversify across Indian and US markets?",
        "What are the pros and cons of investing in Nifty 50 vs S&P 500?",
    ]

    chunks, vectors = load_and_index_knowledge_base()

    for q in questions:
        print("=" * 80)
        print("Question:", q)
        top_chunks = retrieve(q, chunks, vectors, top_k=3)
        if not top_chunks:
            print("No chunks retrieved.")
            continue
        for i, c in enumerate(top_chunks, 1):
            print(f"\n--- Chunk {i} ---")
            print(textwrap.fill(c, width=80))
        print("\nMark how many of these top-3 chunks are relevant to the question.\n")


if __name__ == "__main__":
    main()

import textwrap

from utils.rag_utils import load_and_index_knowledge_base, retrieve


def main():
    """Tiny helper script to inspect RAG retrieval for a few queries.

    Run with:
        python eval_rag.py
    and manually judge how relevant the retrieved chunks are (Precision@K).
    """
    questions = [
        "Explain the key differences between NSE/BSE and US markets.",
        "What are the main stock indices in Indian markets?",
        "How can a beginner diversify across Indian and US markets?",
    ]

    chunks, vectors = load_and_index_knowledge_base()

    for q in questions:
        print("=" * 80)
        print("Question:", q)
        top_chunks = retrieve(q, chunks, vectors, top_k=3)
        if not top_chunks:
            print("No chunks retrieved.")
            continue
        for i, c in enumerate(top_chunks, 1):
            print(f"\n--- Chunk {i} ---")
            print(textwrap.fill(c, width=80))
        print("\nMark how many of these top-3 chunks are relevant to the question.\n")


if __name__ == "__main__":
    main()

