---
title: GitLab Handbook Assistant
emoji: 📘
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# GitLab Handbook Assistant: RAG with measured answers

A chatbot that answers questions about GitLab's people policies from 48 pages of the public [GitLab Handbook](https://handbook.gitlab.com/handbook/), **cites the exact section** behind every claim, and **says "I don't know" when the handbook doesn't cover the question**. It's tested on a 51-question set written before any tuning, with every verdict checked by hand.

**Live demo:** _link added after deploying to Hugging Face Spaces_

[**Watch the 50-second demo (MP4)**](demo/rag-chatbot-demo.mp4): a real answer with numbered citations, a pulled source card with the supporting sentence highlighted, a refusal for an out-of-scope question, and the published eval results. Every screen is from a real run.

## Results

<!-- RESULTS:START -->
| Metric (51 frozen questions) | Baseline: embeddings + plain prompt | **Final: hybrid search + grounded prompt** |
|---|---|---|
| Answer accuracy (fully correct) | 82% (32/39) | **82% (32/39)** |
| Correct or partially correct | 95% (37/39) | **97% (38/39)** |
| Cites the right handbook page | 95% (37/39) | **97% (38/39)** |
| Retrieval recall@6 | 95% (37/39) | **100% (39/39)** |
| False refusals on answerable questions | 0% (0/39) | **0% (0/39)** |
| Correct "I don't know" on out-of-scope questions | 92% (11/12) | **100% (12/12)** |
| Judge verdicts changed by human review | 2 | 2 |

Full per-question report: [`eval/results/results.md`](eval/results/results.md), or `/results` in the running app.
<!-- RESULTS:END -->

How these were measured:
- **Test set:** [`eval/questions.yaml`](eval/questions.yaml) has 39 answerable questions (6 need two sections or two pages combined) and 12 questions the handbook doesn't answer. Every gold answer was copied from the pinned pages, and every "unanswerable" question was confirmed absent by searching the corpus. That check caught four I'd wrongly assumed were missing (pet insurance, phone bills, relocation costs, sabbaticals).
- **Scoring:** answers come from `openai/gpt-oss-120b`. A different model family (`qwen/qwen3.8-27b`) judges each answer against the gold answer **and the passages it cited**, so true extra details aren't penalised. Then every verdict was read by hand; overrides and their reasons are in [`eval/review.yaml`](eval/review.yaml) and counted in the report.
- **Baseline vs final** run on the same frozen set. Since the set was also used to compare the two setups, treat the final numbers as optimistic for unseen questions.

What I learned from the failures:
- **Hybrid search can surface a near-duplicate policy.** For "daily meal limit when traveling", keyword search pulled the *Sponsored Travel* per-diem rules (travel billed to customers), and the model answered from those instead of the $120/day rule. Part of the cause is chunking: the short "Meals" section was merged into the chunk before it, so the $120 rule sits under the heading "Self Stay Incentive Policy". Fixing that is the next improvement, re-measured on the same set.
- **LLM judges need the evidence.** My first judge only saw a short gold answer and marked correct, more detailed answers as wrong. Giving it the cited passages fixed most of that, and hand review caught a judge bug where passages were renumbered.
- **Free-tier limits shape the design.** Groq's free tier allows 200k tokens a day for gpt-oss-120b, about 60 answers. The eval can't run in one day, and the live demo falls back to `gpt-oss-20b` (separate quota) and says so on the page.

## How it works

```
question ──► hybrid search ─────────────► top 6 chunks ──► gpt-oss-120b ──► answer with [n] citations
             • bge-small embeddings (meaning)                 "use only these sources;
             • BM25 (exact terms like "401(k)")               otherwise say I don't know"
             • merged with reciprocal rank fusion
```

1. **Ingest** ([`rag/fetch.py`](rag/fetch.py), [`rag/ingest.py`](rag/ingest.py)): download 48 handbook pages at a pinned commit, strip Hugo front matter, shortcodes and HTML, split at headings into 818 chunks of about 140 words, and embed them locally with `BAAI/bge-small-en-v1.5` (fastembed, no GPU).
2. **Retrieve** ([`rag/retrieve.py`](rag/retrieve.py)): embedding similarity plus BM25, merged with reciprocal rank fusion. Numpy holds the whole index in memory, so no vector database is needed at this size.
3. **Answer** ([`rag/answer.py`](rag/answer.py)): a grounded prompt that cites every sentence, refuses with a fixed phrase when the sources don't cover the question, and doesn't apply one country's rules to another.
4. **Web app** ([`server.py`](server.py), [`static/`](static/)): FastAPI plus a hand-built "card catalog" page. Each claim is numbered to a catalog card showing the handbook path and the cited sentence highlighted; refusals are stamped "Not held in this collection"; `/results` shows the full evaluation. Rate limits per visitor and per day.

## Run it locally

Needs [uv](https://docs.astral.sh/uv/) and a free [Groq API key](https://console.groq.com/keys).

```bash
cp .env.example .env               # then put your key in GROQ_API_KEY
uv sync
uv run uvicorn server:app --port 8000   # open http://localhost:8000
```

Rebuild the data and re-run the evaluation:

```bash
uv run python -m rag.fetch          # download the pinned pages
uv run python -m rag.ingest         # build index/ (chunks + embeddings)
uv run python eval/run_eval.py run baseline
uv run python eval/run_eval.py run final
uv run python eval/run_eval.py report   # writes eval/results/results.md
uv run pytest
```

## Deploy (Hugging Face Spaces, free)

1. Create a Space with the **Docker** SDK and push this repository to it (the YAML block at the top of this README configures it).
2. In the Space settings, add a secret `GROQ_API_KEY`.

The image downloads the embedding model during the build, so the first visitor doesn't wait.

## Project layout

```
rag/          fetch, ingest, retrieve, answer
eval/         questions.yaml (frozen test set), run_eval.py, review.yaml, results/
static/       the web page (HTML, CSS, JS; no build step)
server.py     FastAPI app
data/         the handbook pages used, with SOURCES.md
index/        chunks.jsonl + embeddings.npy
```

## Credits

Handbook content © GitLab, licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [`data/SOURCES.md`](data/SOURCES.md). This project is not affiliated with GitLab. Code is MIT licensed.
