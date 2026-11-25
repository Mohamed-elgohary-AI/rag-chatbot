"""Downloads the handbook pages this project answers from, pinned to one commit.

Run: uv run python -m rag.fetch
Writes data/raw/*.md and data/SOURCES.md.
"""
import json
import urllib.parse
from pathlib import Path

import requests

PROJECT = "gitlab-com/content-sites/handbook"
COMMIT = "1829d4aee16b5d14cb4f6b90f8e29bda84fc16a1"  # handbook main on 2026-11-23
SITE = "https://handbook.gitlab.com"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# Whole folders (every .md inside) and single pages, all under content/handbook/.
FOLDERS = [
    "people-group/time-off-and-absence",
    "people-group/general-onboarding",
    "people-group/offboarding",
    "total-rewards/benefits",
    "total-rewards/compensation",
    "finance/travel",
]
PAGES = [
    "finance/expenses.md",
    "finance/spending-company-money.md",
    "finance/payroll.md",
    "total-rewards/incentives.md",
    "total-rewards/stock-options.md",
    "people-group/relocation.md",
    "people-group/visas.md",
    "people-group/contracts-probation-periods.md",
    "people-group/promotions-transfers.md",
    "people-group/anti-harassment.md",
    "people-group/acceptable-use-policy.md",
    "people-group/celebrations.md",
    "people-group/team-member-relations.md",
]


def api(endpoint: str, **params) -> requests.Response:
    project = urllib.parse.quote(PROJECT, safe="")
    r = requests.get(f"https://gitlab.com/api/v4/projects/{project}/{endpoint}", params=params, timeout=30)
    r.raise_for_status()
    return r


def list_folder(folder: str) -> list[str]:
    files, page = [], 1
    while True:
        batch = api("repository/tree", path=f"content/handbook/{folder}", ref=COMMIT,
                    recursive="true", per_page=100, page=page).json()
        files += [f["path"].removeprefix("content/handbook/") for f in batch
                  if f["type"] == "blob" and f["name"].endswith(".md")]
        if len(batch) < 100:
            return files
        page += 1


def page_url(rel: str) -> str:
    """content path -> live handbook URL (Hugo: _index.md is the folder page)."""
    rel = rel.removesuffix(".md").removesuffix("_index").rstrip("/")
    return f"{SITE}/handbook/{rel}/"


def main() -> None:
    rels = sorted({p for f in FOLDERS for p in list_folder(f)} | set(PAGES))
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = []
    for rel in rels:
        file = urllib.parse.quote(f"content/handbook/{rel}", safe="")
        text = api(f"repository/files/{file}/raw", ref=COMMIT).text
        name = rel.replace("/", "__")
        (RAW / name).write_text(text, encoding="utf-8")
        manifest.append({"file": name, "path": rel, "url": page_url(rel)})
        print(f"{len(text):>7} chars  {rel}")

    (RAW / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    lines = [
        "# Sources",
        "",
        f"Pages from the [GitLab Handbook]({SITE}/handbook/), taken from "
        f"[`{PROJECT}`](https://gitlab.com/{PROJECT}) at commit "
        f"[`{COMMIT[:8]}`](https://gitlab.com/{PROJECT}/-/tree/{COMMIT}).",
        "",
        "The handbook is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). "
        "The copies in `data/raw/` are unchanged; this project only splits and indexes them.",
        "",
        f"{len(manifest)} pages:",
        "",
        *[f"- [{m['path']}]({m['url']})" for m in manifest],
    ]
    (ROOT / "data" / "SOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{len(manifest)} pages saved to {RAW}")


if __name__ == "__main__":
    main()
