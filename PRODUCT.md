# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: recruiters and hiring managers evaluating this as a portfolio project. They open the demo for a few minutes, try one or two policy questions (often the suggested ones), click a citation to see whether it holds up, test whether it refuses an out-of-scope question, and look for proof of rigour: how the answers were measured.

Secondary: anyone curious about GitLab's people policies (time off, benefits, expenses, travel, onboarding, offboarding, equity) who wants a quick, sourced answer.

## Product Purpose

A retrieval-augmented chatbot that answers questions from 48 pages of the public GitLab Handbook (people policies), pinned to one handbook commit. Success for the portfolio: a visitor leaves convinced the author can build RAG that is grounded, checkable and honestly measured, not just a chat box on top of an LLM.

## Positioning

Checkable, honest answers. Every claim links to the exact handbook passage it came from; when the handbook doesn't cover a question it says "I don't know based on the handbook" instead of guessing; and its accuracy is measured on a frozen 51-question test set (39 answerable, 12 unanswerable) with an independent LLM judge and every verdict reviewed by hand, published per question.

## Operating Context

- Visitors arrive from a portfolio, CV or LinkedIn link, on desktop or phone, and stay a few minutes.
- Answers take roughly 10-40 seconds on the free tier.
- The evaluation report (per-question verdicts, baseline vs final) is part of what a recruiter evaluates.

## Capabilities and Constraints

- Answers: `openai/gpt-oss-120b` on Groq's free tier. When its daily quota (200k tokens) runs out, the live demo falls back to `openai/gpt-oss-20b` and must say so; measured numbers always refer to the main model.
- Retrieval: hybrid search (bge-small embeddings + BM25, reciprocal rank fusion), top 6 chunks, 818 chunks from 48 pages.
- Rate limits: 20 questions per visitor per hour, 500 per day; questions 3-500 characters.
- Hosting: free Hugging Face Spaces (Docker). Must stay deployable for free.
- Frontend: FastAPI serves a static HTML/CSS/JS page; API is `POST /api/ask`, `GET /api/stats`, `GET /results`.
- Scope is fixed to the 48 pages listed in `data/SOURCES.md`; the handbook is not live-synced.

## Brand Commitments

- Not affiliated with GitLab: no GitLab logos, wordmarks or brand styling; the product name may say "GitLab Handbook" descriptively.
- Handbook content is credited as © GitLab under CC BY-SA 4.0, with a link to the license.
- Author: Mohamed Elgohary.

## Evidence on Hand

- Real evaluation results: `eval/results/results.md`, `eval/results/summary.json`, per-question rows in `eval/results/*.jsonl`, human overrides in `eval/review.yaml`.
- The frozen test set: `eval/questions.yaml`.
- The source pages and attribution: `data/raw/`, `data/SOURCES.md`.
- No users, testimonials, usage numbers or third-party endorsements exist; none may be invented. Accuracy figures must come only from the eval files.

## Product Principles

1. Evidence over assertion: every answer shows where it came from, and checking it must be easy.
2. Honest limits: refusing is a feature, shown as clearly as an answer; the backup model and known failures are disclosed.
3. Measured, not claimed: numbers on the page come from the published evaluation and link to it.
4. Respect the visitor's few minutes: the first question and the proof of rigour are reachable immediately.
