"""Finds the handbook chunks most relevant to a question.

Hybrid search: embedding similarity (meaning) + BM25 (exact words like "401(k)" or "Modern Health"),
merged with reciprocal rank fusion.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from rag.ingest import EMBED_MODEL, INDEX, embed_text

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # recommended for bge queries
CANDIDATES = 30   # how deep each method looks before fusing
RRF_K = 60        # standard reciprocal-rank-fusion constant


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:\([a-z0-9]+\))?", text.lower())


@lru_cache(maxsize=1)
def load_index(index_dir: Path = INDEX):
    chunks = [json.loads(line) for line in open(index_dir / "chunks.jsonl", encoding="utf-8")]
    vectors = np.load(index_dir / "embeddings.npy")
    bm25 = BM25Okapi([tokenize(embed_text(c)) for c in chunks])
    return chunks, vectors, bm25


@lru_cache(maxsize=1)
def embedder():
    from fastembed import TextEmbedding
    return TextEmbedding(EMBED_MODEL)


def search(question: str, k: int = 6, mode: str = "hybrid") -> list[dict]:
    """Returns the top k chunks, best first. mode: "hybrid" or "vector"."""
    chunks, vectors, bm25 = load_index()
    q = next(iter(embedder().embed([QUERY_PREFIX + question])))
    dense = vectors @ (q / np.linalg.norm(q))
    dense_rank = np.argsort(-dense)[:CANDIDATES]
    if mode == "vector":
        top = dense_rank[:k]
    else:
        sparse_rank = np.argsort(-bm25.get_scores(tokenize(question)))[:CANDIDATES]
        fused: dict[int, float] = {}
        for ranking in (dense_rank, sparse_rank):
            for pos, idx in enumerate(ranking):
                fused[int(idx)] = fused.get(int(idx), 0.0) + 1.0 / (RRF_K + pos + 1)
        top = sorted(fused, key=fused.get, reverse=True)[:k]
    return [{**chunks[i], "similarity": float(dense[i])} for i in top]
