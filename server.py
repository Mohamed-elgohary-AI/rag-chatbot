"""Web app: FastAPI serves the chat page and a small JSON API.

Run locally:  uv run uvicorn server:app --port 8000
"""
import json
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rag.answer import MODEL, answer
from rag.retrieve import embedder, load_index

ROOT = Path(__file__).resolve().parent
MAX_CHARS = 500
PER_IP_LIMIT, PER_IP_WINDOW = 20, 3600   # 20 questions per visitor per hour
DAILY_LIMIT = 500                        # whole demo per day; protects the free Groq quota

app = FastAPI(title="GitLab Handbook Assistant", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
hits: dict[str, deque] = defaultdict(deque)
daily = {"day": time.strftime("%Y-%m-%d"), "count": 0}


@app.on_event("startup")
def warm_up() -> None:
    load_index()
    embedder()


class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=MAX_CHARS)


def client_ip(request: Request) -> str:
    # The host's proxy appends the real address at the END of X-Forwarded-For; earlier entries come from
    # the visitor and can be faked to dodge the per-visitor limit.
    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",")[-1].strip() or (request.client.host if request.client else "unknown")


def check_limits(ip: str) -> None:
    now, today = time.time(), time.strftime("%Y-%m-%d")
    if daily["day"] != today:
        daily.update(day=today, count=0)
        for old in [k for k, q in hits.items() if not q or now - q[-1] > PER_IP_WINDOW]:
            del hits[old]  # forget visitors with nothing left in the window, so `hits` doesn't grow forever
    if daily["count"] >= DAILY_LIMIT:
        raise HTTPException(429, "The demo has reached its daily limit. Please try again tomorrow.")
    q = hits[ip]
    while q and now - q[0] > PER_IP_WINDOW:
        q.popleft()
    if len(q) >= PER_IP_LIMIT:
        raise HTTPException(429, f"You've asked {PER_IP_LIMIT} questions this hour. Please try again later.")
    q.append(now)
    daily["count"] += 1


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.post("/api/ask")
def ask(body: Ask, request: Request) -> dict:
    check_limits(client_ip(request))
    try:
        r = answer(body.question.strip(), fallback=True)
    except Exception as e:  # Groq down or rate-limited: a clear message instead of a stack trace
        raise HTTPException(503, "The answer service is busy right now. Please try again in a minute.") from e
    return {
        "answer": r["answer"],
        "refused": r["refused"],
        "backup_model": r["model"] != MODEL,
        "citations": [
            {"n": c["n"], "title": c["title"], "section": c["heading"].split(" > ")[-1] if c["heading"] else "",
             "url": c["url"], "text": c["text"]}
            for c in sorted(r["citations"], key=lambda c: c["n"])
        ],
    }


@app.get("/results")
def results_page() -> FileResponse:
    return FileResponse(ROOT / "static" / "results.html")


@app.get("/api/results")
def results() -> dict:
    """The evaluation report as data (written by eval/run_eval.py report): headline numbers and every verdict."""
    f = ROOT / "eval" / "results" / "results.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
