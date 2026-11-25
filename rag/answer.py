"""Answers a question from the retrieved handbook chunks, with numbered citations."""
import os
import re
from functools import lru_cache

from dotenv import load_dotenv

from rag.retrieve import search

MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "openai/gpt-oss-20b"  # separate free-tier quota; used by the live demo only when MODEL is rate-limited
REFUSAL = "I don't know based on the handbook."

PROMPTS = {
    # Baseline: a typical first attempt.
    "plain": (
        "You answer questions about GitLab's company handbook. "
        "Use the numbered sources below and cite them like [1]."
    ),
    # Final: grounded, cites every claim, and refuses when the sources don't cover the question.
    "grounded": (
        "You answer questions about GitLab's company handbook, using ONLY the numbered sources provided.\n"
        "- Every factual sentence must end with the source number(s) it comes from, like [2] or [1][3].\n"
        "- Do not use outside knowledge, and do not guess. If the sources do not contain the answer, reply with "
        f"exactly: {REFUSAL}\n"
        "- If the sources answer only part of the question, answer that part and say what the handbook does not cover.\n"
        "- Answers about one country or entity must not be applied to others.\n"
        "- Be concise: a few sentences or a short list."
    ),
}


@lru_cache(maxsize=1)
def client():
    from groq import Groq
    load_dotenv()
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set. Put it in .env (local) or the app's secrets (Streamlit Cloud).")
    return Groq(api_key=key, max_retries=6)  # the SDK backs off and retries on 429 rate limits


def format_sources(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{i}] {c['title']}{' > ' + c['heading'] if c['heading'] else ''}\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )


def normalize_citations(text: str) -> str:
    """gpt-oss sometimes cites in its native style, 【1†L1-L3】; turn that into [1]."""
    return re.sub(r"【(\d+)(?:†[^】]*)?】", r"[\1]", text)


def cited_numbers(text: str, n_sources: int) -> list[int]:
    """Source numbers cited as [n] (also [1, 3] or [1][3]), in order of first use, ignoring invalid ones."""
    found = []
    for group in re.findall(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]", text):
        for num in re.split(r"\s*[,–-]\s*", group):
            n = int(num)
            if 1 <= n <= n_sources and n not in found:
                found.append(n)
    return found


def is_refusal(text: str) -> bool:
    return text.strip().lower().startswith("i don't know") or text.strip().lower().startswith("i do not know")


def answer(question: str, mode: str = "final", k: int = 6, fallback: bool = False) -> dict:
    """mode "final": hybrid search + grounded prompt. mode "baseline": vector search + plain prompt.

    fallback=True (the live demo): if the main model is rate-limited, answer with FALLBACK_MODEL instead.
    The evaluation never uses the fallback, so the reported numbers are always for MODEL.
    """
    from groq import RateLimitError

    chunks = search(question, k=k, mode="hybrid" if mode == "final" else "vector")
    messages = [
        {"role": "system", "content": PROMPTS["grounded" if mode == "final" else "plain"]},
        {"role": "user", "content": f"Sources:\n\n{format_sources(chunks)}\n\nQuestion: {question}"},
    ]
    model = MODEL
    try:
        api = client().with_options(max_retries=1) if fallback else client()
        resp = api.chat.completions.create(model=MODEL, temperature=0, messages=messages)
    except RateLimitError:
        if not fallback:
            raise
        model = FALLBACK_MODEL
        resp = client().chat.completions.create(model=FALLBACK_MODEL, temperature=0, messages=messages)
    text = normalize_citations((resp.choices[0].message.content or "").strip())
    nums = cited_numbers(text, len(chunks))
    return {
        "question": question,
        "answer": text,
        "refused": is_refusal(text),
        "model": model,
        "citations": [{"n": n, **chunks[n - 1]} for n in nums],
        "sources": chunks,
    }


if __name__ == "__main__":
    import sys
    result = answer(" ".join(sys.argv[1:]) or "How much notice do I need to give before taking PTO?")
    print(result["answer"], "\n")
    for c in result["citations"]:
        print(f"[{c['n']}] {c['title']} > {c['heading']}  {c['url']}")
