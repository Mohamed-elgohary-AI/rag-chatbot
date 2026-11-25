"""Cleans the downloaded pages, splits them into chunks at headings, and embeds them.

Run: uv run python -m rag.ingest
Writes index/chunks.jsonl and index/embeddings.npy.
"""
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
INDEX = ROOT / "index"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
MAX_WORDS = 350   # about 450 tokens
MIN_WORDS = 60    # smaller sections are merged into the next one


def clean_markdown(text: str) -> tuple[str, str]:
    """Returns (title, body) with Hugo front matter, shortcodes and HTML removed."""
    title = ""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if m:
        t = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', m.group(1), re.M)
        title = t.group(1).strip() if t else ""
        text = text[m.end():]
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\{\{[<%].*?[%>]\}\}", "", text, flags=re.S)                # shortcode tags; inner text stays
    text = re.sub(r"<summary>(.*?)</summary>", r"\n**\1**\n", text, flags=re.S)  # FAQ questions
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)                           # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)                       # links -> text
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, text.strip()


def split_sections(body: str) -> list[tuple[list[str], str]]:
    """Splits at #..#### headings. Returns (heading path, text) pairs."""
    sections, stack, buf = [], [], []  # stack holds (level, heading) of the current section's ancestors

    def flush():
        txt = "\n".join(buf).strip()
        if txt:
            sections.append(([h for _, h in stack], txt))
        buf.clear()

    in_code = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        m = None if in_code else re.match(r"^(#{1,4})\s+(.+?)\s*#*\s*$", line)
        if m:
            flush()
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, m.group(2).strip()))
        else:
            buf.append(line)
    flush()
    return sections


def words(text: str) -> int:
    return len(text.split())


def paragraphs(text: str) -> list[str]:
    """Blank-line paragraphs; one that is too long on its own (a big list or table) is split at line breaks."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        if words(para) <= MAX_WORDS:
            out.append(para)
            continue
        group = []
        for line in para.splitlines():
            if group and words("\n".join(group + [line])) > MAX_WORDS:
                out.append("\n".join(group))
                group = []
            group.append(line)
        out.append("\n".join(group))
    return out


def chunk_page(title: str, body: str) -> list[dict]:
    """Groups sections into chunks of at most MAX_WORDS words, splitting long sections at paragraphs."""
    chunks = []
    pending = None  # small section waiting to be merged with the next
    for path, text in split_sections(body):
        heading = " > ".join(path)
        if pending:
            text = f"{pending['heading']}\n{pending['text']}\n\n{heading}\n{text}" if heading else f"{pending['text']}\n\n{text}"
            heading = pending["heading"] or heading
            pending = None
        if words(text) < MIN_WORDS:
            pending = {"heading": heading, "text": text}
            continue
        part = []
        for para in paragraphs(text):
            if part and words("\n\n".join(part + [para])) > MAX_WORDS:
                chunks.append({"heading": heading, "text": "\n\n".join(part)})
                part = part[-1:] if words(part[-1]) < MAX_WORDS // 3 else []  # one short paragraph of overlap
            part.append(para)
        if part:
            chunks.append({"heading": heading, "text": "\n\n".join(part)})
    if pending:
        chunks.append(pending)
    return [{"title": title, **c} for c in chunks if words(c["text"]) >= 15]


def embed_text(chunk: dict) -> str:
    """What gets embedded: page title and heading give the chunk its context."""
    return f"{chunk['title']} > {chunk['heading']}\n{chunk['text']}" if chunk["heading"] else f"{chunk['title']}\n{chunk['text']}"


def main() -> None:
    from fastembed import TextEmbedding

    manifest = json.loads((RAW / "manifest.json").read_text(encoding="utf-8"))
    chunks = []
    for page in manifest:
        title, body = clean_markdown((RAW / page["file"]).read_text(encoding="utf-8"))
        for c in chunk_page(title or page["path"], body):
            anchor = re.sub(r"[^a-z0-9 -]", "", c["heading"].split(" > ")[-1].lower()).replace(" ", "-") if c["heading"] else ""
            chunks.append({"id": len(chunks), "url": page["url"] + (f"#{anchor}" if anchor else ""),
                           "page_url": page["url"], **c})

    model = TextEmbedding(EMBED_MODEL)
    vectors = np.array(list(model.embed([embed_text(c) for c in chunks], batch_size=32)), dtype=np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    INDEX.mkdir(exist_ok=True)
    with open(INDEX / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    np.save(INDEX / "embeddings.npy", vectors)
    sizes = [words(c["text"]) for c in chunks]
    print(f"{len(chunks)} chunks from {len(manifest)} pages | words per chunk: "
          f"median {sorted(sizes)[len(sizes) // 2]}, max {max(sizes)} | vectors {vectors.shape}")


if __name__ == "__main__":
    main()
