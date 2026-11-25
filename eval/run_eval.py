"""Runs the frozen test set and reports how well the chatbot does.

  uv run python eval/run_eval.py run baseline     # embeddings only + plain prompt
  uv run python eval/run_eval.py run final        # hybrid search + grounded prompt
  uv run python eval/run_eval.py rejudge <mode>   # re-score saved answers (no new answers generated)
  uv run python eval/run_eval.py report           # writes eval/results/results.md (applies eval/review.yaml)

Each run saves eval/results/<mode>.jsonl with every answer and verdict, for hand review.
A run resumes where it stopped (Groq's free tier has a daily token limit).
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.answer import MODEL, answer, cited_numbers, client  # noqa: E402
from rag.retrieve import search  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODES = ["baseline", "final"]
# A different model family grades the answers, so the model isn't marking its own work; it also has its own quota.
JUDGE_MODEL = "qwen/qwen3.8-27b"

JUDGE_ANSWERABLE = """You grade a chatbot's answer to a question about a company handbook.
You get the question, a short reference answer, the handbook passages the chatbot cited, and the chatbot's answer.
Judge only the facts, not the style.
- "correct": contains the key facts of the reference, contradicts nothing in it, and any extra details are supported by the cited passages.
- "partial": the key facts it gives are right, but an important part of the reference is missing or vague.
- "incorrect": misses or gets wrong the main point, contradicts the reference, makes claims the cited passages do not support, or declines to answer.
Extra details beyond the reference are fine when the cited passages support them.
Reply with JSON only: {"verdict": "correct" | "partial" | "incorrect", "reason": "<one sentence>"}"""

JUDGE_UNANSWERABLE = """The question below cannot be answered from the company handbook the chatbot uses.
Decide whether the chatbot correctly declined: it says it doesn't know or that the handbook doesn't cover it,
WITHOUT inventing a specific answer. Mentioning related policies is fine as long as it does not claim they answer the question.
Reply with JSON only: {"verdict": "declined" | "answered", "reason": "<one sentence>"}"""


def judge(system: str, user: str) -> dict:
    resp = client().chat.completions.create(
        model=JUDGE_MODEL, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return json.loads(resp.choices[0].message.content)


def page_path(url: str) -> str:
    return url.split("/handbook/", 1)[1].split("#")[0].strip("/")


def score(row: dict, cited_chunks: list[dict]) -> dict:
    """Judges one saved answer. Answerable questions are judged against the reference and the cited text."""
    if row["answerable"]:
        if row["refused"]:
            return {"verdict": "incorrect", "reason": "Declined to answer an answerable question."}
        # Keep each passage's original number, so [5] in the answer matches [5] here.
        sources = "\n\n".join(
            f"[{c['n']}] {c['title']}{' > ' + c['heading'] if c['heading'] else ''}\n{c['text']}" for c in cited_chunks
        ) or "(the answer cited no passages)"
        return judge(JUDGE_ANSWERABLE, f"Question: {row['question']}\n\nReference answer: {row['gold']}\n\n"
                                       f"Cited handbook passages:\n{sources}\n\nChatbot answer: {row['answer']}")
    if row["refused"]:
        return {"verdict": "declined", "reason": "Gave the refusal reply."}
    return judge(JUDGE_UNANSWERABLE, f"Question: {row['question']}\n\nChatbot answer: {row['answer']}")


def load_rows(mode: str) -> list[dict]:
    f = RESULTS / f"{mode}.jsonl"
    return [json.loads(line) for line in open(f, encoding="utf-8")] if f.exists() else []


def run(mode: str) -> None:
    qs = yaml.safe_load(open(HERE / "questions.yaml", encoding="utf-8"))
    RESULTS.mkdir(exist_ok=True)
    done = {r["id"] for r in load_rows(mode)}
    items = [(q, True) for q in qs["answerable"]] + [(q, False) for q in qs["unanswerable"]]
    with open(RESULTS / f"{mode}.jsonl", "a", encoding="utf-8") as out:
        for i, (q, answerable) in enumerate(items, 1):
            if q["id"] in done:
                continue
            r = answer(q["question"], mode=mode)
            row = {"id": q["id"], "question": q["question"], "answerable": answerable, "answer": r["answer"],
                   "refused": r["refused"], "cited_pages": sorted({page_path(c["url"]) for c in r["citations"]}),
                   "retrieved_pages": [page_path(c["url"]) for c in r["sources"]]}
            if answerable:
                gold = set(q["pages"])
                row["gold"], row["gold_pages"] = q["gold"], q["pages"]
                row["retrieval_hit"] = bool(gold & set(row["retrieved_pages"]))
                row["citation_hit"] = bool(gold & set(row["cited_pages"]))
            v = score(row, r["citations"])
            row["verdict"], row["reason"] = v["verdict"], v.get("reason", "")
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            print(f"[{i:2}/{len(items)}] {q['id']} {row['verdict']:9} {q['question'][:70]}", flush=True)


def rejudge(mode: str) -> None:
    """Re-scores saved answers with the current judge. Retrieval is deterministic, so the cited chunks are rebuilt exactly."""
    rows = load_rows(mode)
    for row in rows:
        chunks = search(row["question"], mode="hybrid" if mode == "final" else "vector")
        cited = [{"n": n, **chunks[n - 1]} for n in cited_numbers(row["answer"], len(chunks))]
        v = score(row, cited)
        changed = "  (was " + row["verdict"] + ")" if v["verdict"] != row["verdict"] else ""
        row["verdict"], row["reason"] = v["verdict"], v.get("reason", "")
        print(f"{row['id']} {row['verdict']:9}{changed}", flush=True)
    with open(RESULTS / f"{mode}.jsonl", "w", encoding="utf-8") as out:
        out.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def summarize(rows: list[dict]) -> dict:
    ans = [r for r in rows if r["answerable"]]
    una = [r for r in rows if not r["answerable"]]
    count = lambda rs, v: sum(r["verdict"] == v for r in rs)  # noqa: E731
    pct = lambda n, d: f"{100 * n / d:.0f}% ({n}/{d})" if d else "-"  # noqa: E731
    return {
        "Answer accuracy (correct)": pct(count(ans, "correct"), len(ans)),
        "Correct + partial": pct(count(ans, "correct") + count(ans, "partial"), len(ans)),
        "Citation accuracy": pct(sum(r["citation_hit"] for r in ans), len(ans)),
        "Retrieval recall@6": pct(sum(r["retrieval_hit"] for r in ans), len(ans)),
        "False refusals (answerable)": pct(sum(r["refused"] for r in ans), len(ans)),
        'Correct "I don\'t know" (unanswerable)': pct(count(una, "declined"), len(una)),
    }


def report() -> None:
    review_file = HERE / "review.yaml"
    review = yaml.safe_load(open(review_file, encoding="utf-8")) if review_file.exists() else {}
    runs, overridden = {}, {}
    for mode in MODES:
        f = RESULTS / f"{mode}.jsonl"
        if not f.exists():
            continue
        rows = [json.loads(line) for line in open(f, encoding="utf-8")]
        overrides = (review or {}).get(mode) or {}
        for r in rows:
            if r["id"] in overrides:
                r["judge_verdict"], r["verdict"] = r["verdict"], overrides[r["id"]]["verdict"]
                r["reason"] = f"(human review) {overrides[r['id']].get('note', '')}"
        runs[mode], overridden[mode] = rows, sum(r["id"] in overrides for r in rows)

    names = {"baseline": "Baseline: embeddings only + plain prompt", "final": "Final: hybrid search + grounded prompt"}
    stats = {m: summarize(rows) for m, rows in runs.items()}
    lines = ["# Evaluation results", "",
             f"Answers: `{MODEL}` on Groq. Judge: `{JUDGE_MODEL}` (a different model family), given the cited passages. "
             f"Test set: `eval/questions.yaml` "
             f"({sum(r['answerable'] for r in next(iter(runs.values())))} answerable, "
             f"{sum(not r['answerable'] for r in next(iter(runs.values())))} unanswerable), frozen before tuning.",
             "Verdicts come from an LLM judge and were then reviewed by hand; the overrides are counted below.", "",
             "| Metric | " + " | ".join(names[m] for m in runs) + " |",
             "|---|" + "---|" * len(runs)]
    for metric in next(iter(stats.values())):
        lines.append(f"| {metric} | " + " | ".join(stats[m][metric] for m in runs) + " |")
    lines.append("| Judge verdicts changed by human review | " + " | ".join(str(overridden[m]) for m in runs) + " |")
    for mode, rows in runs.items():
        lines += ["", f"## {names[mode]}", "", "| ID | Verdict | Cited the right page | Question | Why |", "|---|---|---|---|---|"]
        for r in rows:
            cite = ("yes" if r.get("citation_hit") else "no") if r["answerable"] else "-"
            lines.append(f"| {r['id']} | {r['verdict']} | {cite} | {r['question']} | {r['reason'].replace('|', '/')} |")
    (RESULTS / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # The same report as data, for the web app's badge and its /results page.
    keep = ("id", "question", "answerable", "verdict", "reason", "answer", "gold", "cited_pages", "citation_hit")
    headline = {}
    if "final" in runs:
        ans = [r for r in runs["final"] if r["answerable"]]
        una = [r for r in runs["final"] if not r["answerable"]]
        headline = {"answerable": len(ans), "unanswerable": len(una),
                    "correct": sum(r["verdict"] == "correct" for r in ans),
                    "declined": sum(r["verdict"] == "declined" for r in una)}
    (RESULTS / "results.json").write_text(json.dumps({
        "answer_model": MODEL, "judge_model": JUDGE_MODEL, "headline": headline,
        "runs": [{"mode": m, "name": names[m], "metrics": stats[m], "overridden": overridden[m],
                  "rows": [{k: r[k] for k in keep if k in r} for r in rows]} for m, rows in runs.items()],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    if sys.argv[1:2] == ["run"] and sys.argv[2:3] and sys.argv[2] in MODES:
        run(sys.argv[2])
    elif sys.argv[1:2] == ["rejudge"] and sys.argv[2:3] and sys.argv[2] in MODES:
        rejudge(sys.argv[2])
    elif sys.argv[1:2] == ["report"]:
        report()
    else:
        sys.exit(__doc__)
