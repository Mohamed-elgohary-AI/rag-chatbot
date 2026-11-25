from rag.answer import cited_numbers, is_refusal, normalize_citations, REFUSAL
from rag.ingest import MAX_WORDS, chunk_page, clean_markdown, split_sections


def test_clean_markdown_strips_front_matter_shortcodes_and_html():
    raw = '---\ntitle: "Time Off"\ndescription: x\n---\n{{% alert %}}Note{{% /alert %}}\n<details><summary>Can I?</summary>Yes, see [the page](/x/).</details>'
    title, body = clean_markdown(raw)
    assert title == "Time Off"
    assert "{{" not in body and "<" not in body
    assert "Note" in body and "**Can I?**" in body and "Yes, see the page." in body


def test_split_sections_keeps_heading_path_and_ignores_code_blocks():
    body = "## A\ntext a\n### B\ntext b\n```\n# not a heading\n```\n## C\ntext c"
    sections = split_sections(body)
    assert [p for p, _ in sections] == [["A"], ["A", "B"], ["C"]]
    assert "# not a heading" in sections[1][1]


def test_chunks_respect_max_size_and_keep_small_sections():
    long_section = "\n\n".join(" ".join(["word"] * 120) for _ in range(6))
    body = f"## Big\n{long_section}\n## Tiny\nshort text here only\n## Next\n" + " ".join(["more"] * 80)
    chunks = chunk_page("Page", body)
    assert all(len(c["text"].split()) <= MAX_WORDS for c in chunks)
    assert any("short text here only" in c["text"] for c in chunks)  # merged, not dropped


def test_cited_numbers_parses_groups_and_ignores_invalid():
    assert cited_numbers("Yes [2]. Also [1][3] and [2, 4] but not [9].", 6) == [2, 1, 3, 4]


def test_native_gpt_oss_citations_are_normalized():
    assert normalize_citations("Six days【1†L1-L3】【3†L9-L12】.") == "Six days[1][3]."


def test_refusal_detection():
    assert is_refusal(REFUSAL)
    assert is_refusal("I do not know based on the handbook.")
    assert not is_refusal("You get 16 weeks of parental leave [1].")
